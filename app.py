from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2

app = Flask(__name__)
app.secret_key = 'chave_secreta_super_segura_para_o_trabalho' 

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost", 
        port="5433",         
        database="financas", 
        user="postgres", 
        password="postgres"  
    )
    return conn

# Rota Principal (Listagem e Inserção)
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'usuario_logado' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    
    usuario_id = session['usuario_id'] # Pega o ID do usuário logado

    if request.method == 'POST':
        descricao = request.form['descricao']
        data_lancamento = request.form['data_lancamento']
        valor = request.form['valor']
        tipo = request.form['tipo_lancamento']
        situacao = request.form['situacao']

        # INSERE O LANÇAMENTO VINCULADO AO ID DO USUÁRIO
        cur.execute(
            'INSERT INTO lancamento (usuario_id, descricao, data_lancamento, valor, tipo_lancamento, situacao) VALUES (%s, %s, %s, %s, %s, %s)',
            (usuario_id, descricao, data_lancamento, valor, tipo, situacao)
        )
        conn.commit()
        return redirect(url_for('index'))

    # BUSCA APENAS OS LANÇAMENTOS DO USUÁRIO LOGADO
    cur.execute('SELECT id, descricao, data_lancamento, valor, tipo_lancamento, situacao FROM lancamento WHERE usuario_id = %s ORDER BY data_lancamento DESC;', (usuario_id,))
    lancamentos = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('index.html', lancamentos=lancamentos)

# Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        senha = request.form['senha']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, nome FROM usuario WHERE login = %s AND senha = %s AND situacao = %s', (login, senha, 'ATIVO'))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session['usuario_id'] = user[0] # Salva o ID do usuário na sessão (NOVO)
            session['usuario_logado'] = user[1] 
            return redirect(url_for('index'))
        else:
            flash('Login ou senha incorretos!')

    return render_template('login.html')

# Rota de Criação de Usuário
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        login = request.form['login']
        senha = request.form['senha']

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO usuario (nome, login, senha, situacao) VALUES (%s, %s, %s, 'ATIVO')",
                (nome, login, senha)
            )
            conn.commit()
            cur.close()
            conn.close()
            flash('Usuário criado com sucesso! Faça seu login.')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Erro ao criar usuário. O login já pode estar em uso.')
            
    return render_template('cadastro.html')

# Rota de Logout (Sair)
@app.route('/logout')
def logout():
    session.pop('usuario_logado', None)
    session.pop('usuario_id', None) # Limpa o ID da sessão ao sair
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)