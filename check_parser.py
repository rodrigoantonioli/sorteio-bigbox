from app.utils import parse_instagram_comments

# Carrega o conteúdo do arquivo
with open('uploads/posts.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Executa o parser
result = parse_instagram_comments(content, 'eu quero', 30)

# Lista de usuários para verificar
users = [
    'fakeuser1', 'fakeuser2', 'fakeuser3', 'fakeuser4',
    'fakeuser5', 'fakeuser6', 'fakeuser7', 'fakeuser8',
    'fakeuser9', 'fakeuser10', 'fakeuser11'
]

print("Valores reais do parser:")
for user in users:
    tickets = result.get(user, {}).get('tickets', 0)
    print(f"'{user}': {tickets},") 