Write-Host "🔄 Resetando repositório para versão 1.0.0 limpa..." -ForegroundColor Cyan

Write-Host ""
Write-Host "1. Removendo tag v1.0.0 local..." -ForegroundColor Yellow
git tag -d v1.0.0

Write-Host ""
Write-Host "2. Removendo tag v1.0.0 remota..." -ForegroundColor Yellow
git push origin :refs/tags/v1.0.0

Write-Host ""
Write-Host "3. Criando commit limpo para v1.0.0..." -ForegroundColor Yellow
git add -A
git commit -m "🚀 v1.0.0 - Sistema de Sorteios Big Box & UltraBox

✨ Primeira versão oficial do sistema
- Sistema completo de sorteios Big Box & UltraBox
- Interface moderna e responsiva Bootstrap 5
- Gestão facilitada de lojas, assistentes e colaboradores
- Sistema de prêmios com pool geral e atribuição
- Sorteios automáticos semanais (BIG + ULTRA)
- Histórico completo e transparente
- Zona vermelha para operações administrativas
- Controle de acesso por roles (Admin/Assistente)
- Upload de colaboradores via Excel
- Deploy configurado para Render.com

🎯 Sistema completo e pronto para Festival Na Praia 2025!"

Write-Host ""
Write-Host "4. Criando nova tag v1.0.0..." -ForegroundColor Yellow
git tag -a v1.0.0 -m "v1.0.0 - Primeira Versão Oficial

🎲 Sistema de Sorteios Big Box & UltraBox - Festival Na Praia 2025

✅ FUNCIONALIDADES COMPLETAS:
• Gestão visual de lojas com dashboard informativo
• Sistema de prêmios com pool geral e atribuição
• Sorteios automáticos semanais com algoritmo anti-repetição
• Upload de colaboradores via planilhas Excel
• Interface responsiva Bootstrap 5
• Controle de acesso seguro por roles
• Histórico completo e auditável
• Zona vermelha para operações admin

🚀 PRIMEIRA VERSÃO OFICIAL - PRONTA PARA PRODUÇÃO!"

Write-Host ""
Write-Host "5. Enviando para GitHub..." -ForegroundColor Yellow
git push origin master
git push origin v1.0.0

Write-Host ""
Write-Host "✅ Repositório resetado e versão 1.0.0 criada com sucesso!" -ForegroundColor Green
Write-Host "🎉 Sistema pronto para produção no Festival Na Praia 2025!" -ForegroundColor Green

Read-Host "Pressione Enter para continuar" 