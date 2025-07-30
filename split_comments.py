#!/usr/bin/env python3
"""
Script para dividir arquivos grandes de comentários do Instagram em partes menores.
Uso: python split_comments.py arquivo_grande.txt
"""

import sys
import os

def split_comments_file(input_file, max_size_mb=10):
    """
    Divide um arquivo de comentários em partes menores.
    
    Args:
        input_file: Caminho para o arquivo de entrada
        max_size_mb: Tamanho máximo de cada parte em MB
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if not os.path.exists(input_file):
        print(f"Erro: Arquivo '{input_file}' não encontrado!")
        return
    
    file_size = os.path.getsize(input_file)
    print(f"Tamanho do arquivo: {file_size / (1024*1024):.2f} MB")
    
    if file_size <= max_size_bytes:
        print("Arquivo já está dentro do limite de tamanho!")
        return
    
    base_name = os.path.splitext(input_file)[0]
    extension = os.path.splitext(input_file)[1]
    
    part_num = 1
    current_size = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        output_file = f"{base_name}_parte_{part_num}{extension}"
        outfile = open(output_file, 'w', encoding='utf-8')
        
        print(f"Criando: {output_file}")
        
        for line in infile:
            line_size = len(line.encode('utf-8'))
            
            # Se adicionar esta linha exceder o limite, crie um novo arquivo
            if current_size + line_size > max_size_bytes and current_size > 0:
                outfile.close()
                print(f"Parte {part_num} concluída: {current_size / (1024*1024):.2f} MB")
                
                part_num += 1
                current_size = 0
                output_file = f"{base_name}_parte_{part_num}{extension}"
                outfile = open(output_file, 'w', encoding='utf-8')
                print(f"Criando: {output_file}")
            
            outfile.write(line)
            current_size += line_size
        
        outfile.close()
        print(f"Parte {part_num} concluída: {current_size / (1024*1024):.2f} MB")
    
    print(f"\nArquivo dividido em {part_num} partes!")
    print(f"Agora você pode processar cada parte separadamente no sistema.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python split_comments.py arquivo_comentarios.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    split_comments_file(input_file)