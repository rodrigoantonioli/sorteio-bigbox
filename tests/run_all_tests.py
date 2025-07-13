#!/usr/bin/env python3
"""
Script para executar todos os testes do sistema de sorteios
"""

import unittest
import sys
import os
from io import StringIO

# Adiciona o diretório raiz e o diretório de testes ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def run_all_tests():
    """Executa todos os testes e gera relatório"""
    
    # Descobrir todos os testes
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    top_level_dir = os.path.abspath(os.path.join(start_dir, '..'))
    suite = loader.discover(start_dir=start_dir, pattern='test_*.py', top_level_dir=top_level_dir)
    
    # Executar os testes
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)
    
    # Gerar relatório
    print("=" * 70)
    print("RELATÓRIO DE TESTES - SISTEMA DE SORTEIOS BIGBOX v1.0")
    print("=" * 70)
    print()
    
    # Estatísticas
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    passed = total_tests - failures - errors - skipped
    
    print(f"📊 ESTATÍSTICAS:")
    print(f"   Total de testes executados: {total_tests}")
    print(f"   ✅ Testes aprovados: {passed}")
    print(f"   ❌ Testes falharam: {failures}")
    print(f"   🚨 Erros: {errors}")
    print(f"   ⏭️  Testes ignorados: {skipped}")
    print()
    
    # Percentual de sucesso
    if total_tests > 0:
        success_rate = (passed / total_tests) * 100
        print(f"📈 Taxa de sucesso: {success_rate:.1f}%")
        
        if success_rate >= 95:
            status = "🟢 EXCELENTE"
        elif success_rate >= 85:
            status = "🟡 BOM"
        elif success_rate >= 70:
            status = "🟠 ACEITÁVEL"
        else:
            status = "🔴 CRÍTICO"
        
        print(f"🎯 Status: {status}")
        print()
    
    # Detalhes dos testes
    if failures or errors:
        print("🔍 DETALHES DOS PROBLEMAS:")
        print("-" * 50)
        
        for test, traceback in result.failures:
            print(f"❌ FALHA: {test}")
            print(f"   {traceback}")
            print()
        
        for test, traceback in result.errors:
            print(f"🚨 ERRO: {test}")
            print(f"   {traceback}")
            print()
    
    # Áreas testadas
    print("📋 ÁREAS TESTADAS:")
    print("   ✓ Modelos de dados e banco de dados")
    print("   ✓ Autenticação e autorização")
    print("   ✓ Gestão de lojas")
    print("   ✓ Gestão de colaboradores")
    print("   ✓ Sistema de prêmios")
    print("   ✓ Sistema de sorteios")
    print("   ✓ Dashboards e relatórios")
    print("   ✓ Testes de integração")
    print()
    
    # Funcionalidades testadas
    print("🔧 FUNCIONALIDADES TESTADAS:")
    print("   • CRUD completo de todas as entidades")
    print("   • Controle de acesso por tipo de usuário")
    print("   • Upload de arquivos Excel")
    print("   • Sorteios semanais automatizados")
    print("   • Histórico e auditoria")
    print("   • Integridade de dados")
    print("   • Constraints de banco de dados")
    print("   • Validações de negócio")
    print()
    
    # Ambiente de teste
    print("🏗️  AMBIENTE DE TESTE:")
    print("   • Banco de dados: SQLite em memória")
    print("   • Framework: Flask + SQLAlchemy")
    print("   • Testes: unittest (Python padrão)")
    print("   • Dados: Dados de teste sintéticos")
    print()
    
    # Recomendações
    if success_rate < 100:
        print("💡 RECOMENDAÇÕES:")
        print("   • Revisar os testes que falharam")
        print("   • Verificar se as rotas estão implementadas")
        print("   • Validar se os formulários estão funcionando")
        print("   • Testar manualmente as funcionalidades")
        print()
    else:
        print("🎉 PARABÉNS!")
        print("   Todos os testes passaram! O sistema está pronto para homologação.")
        print()
    
    print("=" * 70)
    print("Relatório gerado em:", __file__)
    print("=" * 70)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1) 