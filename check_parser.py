from app.utils import parse_instagram_comments

# Carrega o conteúdo do arquivo
with open('uploads/posts.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Executa o parser
result = parse_instagram_comments(content, 'eu quero', 30)

# Lista de usuários para verificar
users = [
    'rivaldo.rodrigues_', 'van3ssasousa', 'ricardoloiola', 'luenymello', 
    'elane_oliveiralima', 'patymorena1', 'sr_batista_', 'niveabelfort_', 
    'vitorr_hgoo', 'lucasdesousa01', 'gildenir.muniz'
]

print("Valores reais do parser:")
for user in users:
    tickets = result.get(user, {}).get('tickets', 0)
    print(f"'{user}': {tickets},") 