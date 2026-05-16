# 📋 Sistema de Ficha Técnica PRO

Sistema profissional de gestão de custos e precificação para empresas de alimentos.

## 🚀 Deploy Online (Streamlit Cloud)

### Passo 1: GitHub
1. Crie conta no GitHub (se não tiver)
2. Crie novo repositório chamado `ficha-tecnica-pro`
3. Faça upload de todos os arquivos deste projeto

### Passo 2: Streamlit Cloud
1. Acesse: https://share.streamlit.io
2. Faça login com GitHub
3. Clique em "New app"
4. Selecione seu repositório: `ficha-tecnica-pro`
5. Main file: `app.py`
6. Clique em "Deploy"

Pronto! Seu app estará em: `https://SEU-USUARIO-ficha-tecnica-pro.streamlit.app`

### Usar Seu Domínio
1. No Streamlit Cloud, vá em Settings
2. Configure Custom subdomain
3. No seu domínio, crie CNAME apontando para o Streamlit

---

## 💻 Rodar Localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

Abre em: http://localhost:8501

---

## 📁 Estrutura

- `app.py` - Aplicação principal
- `models.py` - Banco de dados
- `exportacao_premium.py` - Excel/PDF
- `gerenciador_logos.py` - Logos
- `requirements.txt` - Dependências

---

## 🎯 Funcionalidades

✅ Gestão de Clientes (com logos)
✅ Controle de Insumos
✅ Custos Operacionais
✅ Fichas Técnicas (receitas)
✅ Precificação Automática
✅ Exportação Excel/PDF Premium

---

Desenvolvido com ❤️ para profissionais de alimentos
