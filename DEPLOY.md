# 🚀 GUIA COMPLETO DE DEPLOY

## ✅ OPÇÃO 1: Streamlit Cloud (GRÁTIS - RECOMENDADO)

### Passo a Passo:

#### 1. Preparar GitHub
```bash
# Crie conta no GitHub: https://github.com/signup

# Crie novo repositório:
- Nome: ficha-tecnica-pro
- Público ou Privado
- Não adicione README (já temos)
```

#### 2. Upload dos Arquivos
```bash
# Método 1: Via site GitHub
1. Vá no repositório
2. Clique em "Add file" → "Upload files"
3. Arraste TODOS os arquivos do projeto
4. Commit

# Método 2: Via Git (se tem instalado)
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/SEU_USUARIO/ficha-tecnica-pro.git
git push -u origin main
```

#### 3. Deploy no Streamlit Cloud
```
1. Acesse: https://share.streamlit.io
2. Login com GitHub
3. Clique "New app"
4. Selecione:
   - Repository: ficha-tecnica-pro
   - Branch: main
   - Main file path: app.py
5. Clique "Deploy!"

AGUARDE 5-10 MINUTOS

Pronto! URL: https://SEU-USUARIO-ficha-tecnica-pro.streamlit.app
```

#### 4. Usar Seu Domínio (Opcional)
```
No Streamlit Cloud:
1. Settings → General
2. Custom subdomain: escolha nome
3. URL fica: https://NOME.streamlit.app

Para domínio próprio (app.seusite.com):
1. No seu provedor de domínio (Registro.br, GoDaddy, etc)
2. Crie CNAME:
   Nome: app
   Valor: NOME.streamlit.app
3. Aguarde propagação (até 48h)
```

---

## ✅ OPÇÃO 2: Heroku (Cloud)

```bash
# 1. Crie conta: https://heroku.com

# 2. Instale Heroku CLI
# Windows: baixe instalador
# Linux/Mac: curl https://cli-assets.heroku.com/install.sh | sh

# 3. Login
heroku login

# 4. Crie arquivo Procfile
echo "web: sh setup.sh && streamlit run app.py" > Procfile

# 5. Crie setup.sh
cat > setup.sh << 'EOF'
mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
EOF

# 6. Deploy
heroku create seu-app-ficha-tecnica
git push heroku main
heroku open
```

---

## ✅ OPÇÃO 3: Seu Servidor (VPS/Dedicado)

### Requisitos:
- Ubuntu 20.04+ ou similar
- Python 3.9+
- Nginx

### Instalação:

```bash
# 1. Conecte no servidor via SSH
ssh usuario@seu-servidor.com

# 2. Instale Python e dependências
sudo apt update
sudo apt install python3-pip python3-venv nginx -y

# 3. Clone ou faça upload do projeto
git clone https://github.com/SEU_USUARIO/ficha-tecnica-pro.git
cd ficha-tecnica-pro

# 4. Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 5. Instale dependências
pip install -r requirements.txt

# 6. Teste local
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

# 7. Configure Nginx (proxy reverso)
sudo nano /etc/nginx/sites-available/ficha-tecnica

# Cole:
server {
    listen 80;
    server_name app.seudominio.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}

# Ative
sudo ln -s /etc/nginx/sites-available/ficha-tecnica /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 8. Rodar permanentemente (systemd)
sudo nano /etc/systemd/system/ficha-tecnica.service

# Cole:
[Unit]
Description=Ficha Tecnica Streamlit
After=network.target

[Service]
User=usuario
WorkingDirectory=/home/usuario/ficha-tecnica-pro
ExecStart=/home/usuario/ficha-tecnica-pro/venv/bin/streamlit run app.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target

# Ative
sudo systemctl enable ficha-tecnica
sudo systemctl start ficha-tecnica
sudo systemctl status ficha-tecnica

# 9. SSL (HTTPS) com Certbot
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d app.seudominio.com
```

---

## 📱 Testar o Sistema Online

Depois do deploy, teste:

1. Acesse a URL do seu app
2. Cadastre um cliente
3. Adicione insumos
4. Crie uma ficha técnica
5. Exporte Excel/PDF

---

## 🔒 Segurança em Produção

### Streamlit Cloud:
- Já vem seguro (HTTPS automático)
- Dados no SQLite persistem

### Servidor próprio:
```bash
# 1. Firewall
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# 2. Backup automático
# Crie script: /home/usuario/backup.sh
#!/bin/bash
cp /home/usuario/ficha-tecnica-pro/ficha_tecnica.db /home/usuario/backups/ficha_$(date +%Y%m%d).db

# Cron diário
crontab -e
# Adicione:
0 2 * * * /home/usuario/backup.sh
```

---

## 📊 Monitoramento

### Streamlit Cloud:
- Veja logs em: Manage app → Logs
- Métricas: Settings → Analytics

### Servidor:
```bash
# Logs do Streamlit
sudo journalctl -u ficha-tecnica -f

# Status
sudo systemctl status ficha-tecnica

# Reiniciar
sudo systemctl restart ficha-tecnica
```

---

## 🆘 Problemas Comuns

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Port already in use"
```bash
# Mude porta em app.py ou:
streamlit run app.py --server.port 8502
```

### "Database locked"
```bash
# Permissões
chmod 666 ficha_tecnica.db
```

---

## 📞 Suporte

Precisa de ajuda? 
- Email: contato@exemplo.com
- Issues: https://github.com/SEU_USUARIO/ficha-tecnica-pro/issues
