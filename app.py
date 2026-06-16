import os

# =====================================================================
# >>> DEMONSTRACAO DE FALHA NO PIPELINE (Tarefa Final - GCS) <<<
#
# Para demonstrar que o pipeline BLOQUEIA codigo com erro e NAO segue
# para o deploy, descomente a linha abaixo, faca commit e push na
# branch 'homolog'. O flake8 acusa E999 (SyntaxError) e os 20 testes
# falham no "from app import app" -> deploy fica como "Skipped".
# Depois, comente novamente e faca push -> pipeline volta a passar.
# =====================================================================
# def funcao_quebrada(:

from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
import psycopg2
from flask_mail import Mail, Message
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'chave_secreta_tarefa_3')

# --- ISOLAMENTO DE SESSAO ENTRE AMBIENTES ---
# Homolog e Prod rodam no mesmo dominio (177.44.248.72), separados so
# pelo caminho (/homolog e /prod). Sem isto, o cookie de sessao de um
# sobrescreve o do outro e o login "cai" ao trocar de ambiente.
# Cada ambiente usa um cookie com nome e caminho proprios.
_prefix = os.environ.get('APP_PREFIX', '')
if _prefix:
    app.config['SESSION_COOKIE_PATH'] = _prefix
    app.config['SESSION_COOKIE_NAME'] = 'session_' + _prefix.strip('/')

# --- CONFIGURAÇÃO DE E-MAIL ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'tiago.patzlaff@universo.univates.br'
app.config['MAIL_PASSWORD'] = 'senha'
mail = Mail(app)

# Permite servir atras do NGINX em /homolog ou /prod (via APP_PREFIX).
# Sem APP_PREFIX (local e nos testes), nao tem efeito.
class PrefixMiddleware:
    def __init__(self, wsgi_app, prefix=''):
        self.wsgi_app = wsgi_app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if self.prefix:
            environ['SCRIPT_NAME'] = self.prefix
            path = environ.get('PATH_INFO', '')
            if path.startswith(self.prefix):
                environ['PATH_INFO'] = path[len(self.prefix):] or '/'
        return self.wsgi_app(environ, start_response)


app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=os.environ.get('APP_PREFIX', ''))


def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        database=os.environ.get("DB_NAME", "financas"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "postgres"),
        port=os.environ.get("DB_PORT", "5432"))

# --- FUNÇÕES DE E-MAIL ---
def enviar_email_notificacao(tipo_acao, descricao, detalhes=""):
    try:
        email_dest = session.get('usuario_email')
        if not email_dest: return
        msg = Message(f'Finanças: Item {tipo_acao}', sender=app.config['MAIL_USERNAME'], recipients=[email_dest])
        
        # Monta o corpo do e-mail
        corpo = f'Olá {session.get("usuario_logado")},\n\nO item "{descricao}" foi {tipo_acao} no seu sistema.'
        
        # Se tiver detalhes (como na edição), adiciona no e-mail
        if detalhes:
            corpo += f'\n\n{detalhes}'
            
        msg.body = corpo
        mail.send(msg)
    except Exception as e:
        print(f"Erro e-mail: {e}")

def enviar_email_com_pdf(pdf_content):
    try:
        email_dest = session.get('usuario_email')
        if not email_dest: return
        msg = Message('Seu Relatório de Finanças PDF', sender=app.config['MAIL_USERNAME'], recipients=[email_dest])
        msg.body = f'Olá {session.get("usuario_logado")},\n\nSegue em anexo o relatório em PDF gerado no sistema.'
        msg.attach("relatorio_financas.pdf", "application/pdf", pdf_content)
        mail.send(msg)
    except Exception as e:
        print(f"Erro e-mail PDF: {e}")

# --- ROTAS PRINCIPAIS (CRUD + PDF) ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'usuario_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Filtros
    data_ini = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    status = request.args.get('status')
    
    query = "SELECT id, descricao, data_lancamento, valor, tipo_lancamento, situacao FROM lancamento WHERE usuario_id = %s"
    params = [session['usuario_id']]
    
    if data_ini: query += " AND data_lancamento >= %s"; params.append(data_ini)
    if data_fim: query += " AND data_lancamento <= %s"; params.append(data_fim)
    if status: query += " AND situacao = %s"; params.append(status)
    query += " ORDER BY data_lancamento DESC"

    # Criar
    if request.method == 'POST':
        desc = request.form['descricao']
        cur.execute('INSERT INTO lancamento (usuario_id, descricao, data_lancamento, valor, tipo_lancamento, situacao) VALUES (%s, %s, %s, %s, %s, %s)',
                    (session['usuario_id'], desc, request.form['data_lancamento'], request.form['valor'], request.form['tipo_lancamento'], request.form['situacao']))
        conn.commit()
        enviar_email_notificacao("CRIADO", desc)
        return redirect(url_for('index'))

    # Ler (Listar)
    cur.execute(query, tuple(params))
    lancamentos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', lancamentos=lancamentos)

# Editar (Update)
# Editar (Update)
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'usuario_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        # 1. Pega os dados ANTIGOS antes de alterar
        cur.execute('SELECT descricao, data_lancamento, valor, tipo_lancamento, situacao FROM lancamento WHERE id=%s AND usuario_id=%s', (id, session['usuario_id']))
        old = cur.fetchone()
        
        # 2. Prepara os dados NOVOS que vieram do formulário
        desc = request.form['descricao']
        data_lanc = request.form['data_lancamento']
        valor = request.form['valor']
        tipo = request.form['tipo_lancamento']
        situacao = request.form['situacao']
        
        # 3. Salva no banco de dados
        cur.execute('UPDATE lancamento SET descricao=%s, data_lancamento=%s, valor=%s, tipo_lancamento=%s, situacao=%s WHERE id=%s AND usuario_id=%s',
                    (desc, data_lanc, valor, tipo, situacao, id, session['usuario_id']))
        conn.commit()
        
        # 4. Compara o antigo com o novo para montar o relatório do e-mail
        mudancas = []
        if old[0] != desc: mudancas.append(f"- Descrição: de '{old[0]}' para '{desc}'")
        if str(old[1]) != data_lanc: mudancas.append(f"- Data: de '{old[1]}' para '{data_lanc}'")
        if float(old[2]) != float(valor): mudancas.append(f"- Valor: de 'R$ {old[2]}' para 'R$ {valor}'")
        if old[3] != tipo: mudancas.append(f"- Tipo: de '{old[3]}' para '{tipo}'")
        if old[4] != situacao: mudancas.append(f"- Situação: de '{old[4]}' para '{situacao}'")
        
        # Só escreve se realmente algo foi mudado
        if mudancas:
            detalhes = "Alterações realizadas:\n" + "\n".join(mudancas)
        else:
            detalhes = "Nenhum valor foi alterado."
        
        # Dispara o e-mail com os detalhes!
        enviar_email_notificacao("EDITADO", desc, detalhes)
        
        cur.close()
        conn.close()
        return redirect(url_for('index'))

    # Se for GET, só mostra o formulário preenchido
    cur.execute('SELECT id, descricao, data_lancamento, valor, tipo_lancamento, situacao FROM lancamento WHERE id=%s AND usuario_id=%s', (id, session['usuario_id']))
    item = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('edit.html', lancamento=item)

# Excluir (Delete)
@app.route('/delete/<int:id>')
def delete(id):
    if 'usuario_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT descricao FROM lancamento WHERE id=%s AND usuario_id=%s', (id, session['usuario_id']))
    item = cur.fetchone()
    
    if item:
        cur.execute('DELETE FROM lancamento WHERE id = %s AND usuario_id = %s', (id, session['usuario_id']))
        conn.commit()
        enviar_email_notificacao("EXCLUÍDO", item[0])
        
    cur.close()
    conn.close()
    return redirect(url_for('index'))

# Exportar PDF
@app.route('/exportar_pdf')
def exportar_pdf():
    if 'usuario_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT descricao, data_lancamento, valor, tipo_lancamento, situacao FROM lancamento WHERE usuario_id = %s ORDER BY data_lancamento DESC', (session['usuario_id'],))
    dados = cur.fetchall()
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "Relatorio de Financas Pessoais", 0, 1, 'C')
    pdf.set_font("Arial", size=10)
    
    pdf.cell(60, 10, "Descricao", 1, 0, 'C')
    pdf.cell(30, 10, "Data", 1, 0, 'C')
    pdf.cell(30, 10, "Valor (R$)", 1, 0, 'C')
    pdf.cell(30, 10, "Tipo", 1, 0, 'C')
    pdf.cell(40, 10, "Situacao", 1, 1, 'C')
    
    for row in dados:
        pdf.cell(60, 10, str(row[0]), 1, 0)
        pdf.cell(30, 10, str(row[1]), 1, 0, 'C')
        pdf.cell(30, 10, str(row[2]), 1, 0, 'R')
        pdf.cell(30, 10, str(row[3]), 1, 0, 'C')
        pdf.cell(40, 10, str(row[4]), 1, 1, 'C')
    
    pdf_out = pdf.output(dest='S').encode('latin-1')
    
    # Envia e-mail com o PDF em anexo
    enviar_email_com_pdf(pdf_out)
    
    response = make_response(pdf_out)
    response.headers.set('Content-Disposition', 'attachment', filename='relatorio_financas.pdf')
    response.headers.set('Content-Type', 'application/pdf')
    return response

# --- ROTAS DE AUTENTICAÇÃO E PERFIL ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        senha = request.form['senha']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, nome, email FROM usuario WHERE login = %s AND senha = %s AND situacao = %s', (login, senha, 'ATIVO'))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session['usuario_id'] = user[0]
            session['usuario_logado'] = user[1] 
            session['usuario_email'] = user[2]
            return redirect(url_for('index'))
        else:
            flash('Login ou senha incorretos!')

    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        login = request.form['login']
        senha = request.form['senha']

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO usuario (nome, login, senha, situacao, email) VALUES (%s, %s, %s, 'ATIVO', %s)",
                (nome, login, senha, email)
            )
            conn.commit()
            cur.close()
            conn.close()
            flash('Usuário criado com sucesso! Faça seu login.')
            return redirect(url_for('login'))
        except Exception:
            flash('Erro ao criar usuário. O login já pode estar em uso.')
            
    return render_template('cadastro.html')

@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if 'usuario_id' not in session: return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        nome = request.form['nome']
        login = request.form['login']
        email = request.form['email']
        senha = request.form['senha']

        cur.execute(
            "UPDATE usuario SET nome = %s, login = %s, email = %s, senha = %s WHERE id = %s",
            (nome, login, email, senha, session['usuario_id'])
        )
        conn.commit()
        
        session['usuario_logado'] = nome
        session['usuario_email'] = email
        flash('Perfil atualizado com sucesso!')

    cur.execute('SELECT id, nome, login, senha, email FROM usuario WHERE id = %s', (session['usuario_id'],))
    usuario = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('perfil.html', usuario=usuario)

@app.route('/logout')
def logout():
    session.pop('usuario_logado', None)
    session.pop('usuario_id', None)
    session.pop('usuario_email', None)
    return redirect(url_for('login'))

# --- A CHAVE NA IGNIÇÃO ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
