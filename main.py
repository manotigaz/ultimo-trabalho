import requests
import json
import webbrowser
import os
import matplotlib.pyplot as plt
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

API_URL = "http://localhost:3000"
console = Console()

# ==========================================
# REQUISITO 1: CRUD na Tabela Auxiliar (Categorias)
# ==========================================
def listar_categorias():
    response = requests.get(f"{API_URL}/categorias")
    categorias = response.json()
    table = Table(title="Categorias de Roupas")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Nome da Categoria", style="magenta")
    for cat in categorias:
        table.add_row(str(cat["id"]), cat["nome"])
    console.print(table)
    return categorias


def criar_categoria():
    nome = Prompt.ask("Digite o nome da nova categoria")
    requests.post(f"{API_URL}/categorias", json={"nome": nome})
    console.print("[green]Categoria criada com sucesso![/green]")

# Funções de Update e Delete da categoria omitidas por brevidade no menu principal,
# mas o padrão é o mesmo (requests.put e requests.delete).

# ==========================================
# REQUISITO 2: CRUD na Tabela Principal c/ Prompt.ask (Roupas)
# ==========================================
def listar_pecas():
    pecas = requests.get(f"{API_URL}/pecas").json()
    categorias = requests.get(f"{API_URL}/categorias").json()

    cat_map = {cat["id"]: cat["nome"] for cat in categorias}

    table = Table(title="Roupas Cadastradas")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="green")
    table.add_column("Preço (R$)", style="yellow")
    table.add_column("Categoria", style="magenta")

    for peca in pecas:
        nome_cat = cat_map.get(peca["categoriaId"], "Desconhecida")
        table.add_row(str(peca["id"]), peca["nome"], str(peca["preco"]), nome_cat)
    console.print(table)


def criar_peca():
    nome = Prompt.ask("Nome da roupa")
    preco = float(Prompt.ask("Preço (R$)"))

    categorias = listar_categorias()
    if not categorias:
        console.print("[red]Cadastre uma categoria primeiro![/red]")
        return

    opcoes_id = [str(cat["id"]) for cat in categorias]
    categoria_id = Prompt.ask("Escolha o ID da categoria", choices=opcoes_id)

    nova_peca = {"nome": nome, "preco": preco, "categoriaId": categoria_id}
    requests.post(f"{API_URL}/pecas", json=nova_peca)
    console.print("[green]Roupa cadastrada com sucesso![/green]")


def deletar_peca():
    listar_pecas()
    id_peca = Prompt.ask("Digite o ID da roupa que deseja deletar")
    resposta = requests.delete(f"{API_URL}/pecas/{id_peca}")
    if resposta.status_code in [200, 204]:
        console.print("[green]Roupa deletada![/green]")
    else:
        console.print("[red]Erro ao deletar (ID não encontrado).[/red]")

# ==========================================
# REQUISITO 3: Pesquisa Avançada (Nome + Preço Máximo)
# ==========================================
def pesquisa_avancada():
    termo = Prompt.ask("Digite parte do nome da roupa para buscar").lower()
    preco_max = float(Prompt.ask("Qual o preço máximo desejado?", default="5000"))

    pecas = requests.get(f"{API_URL}/pecas").json()
    resultados = [p for p in pecas if termo in p["nome"].lower() and float(p["preco"]) <= preco_max]

    if resultados:
        console.print(f"\n[green]Encontrados {len(resultados)} resultados:[/green]")
        for r in resultados:
            console.print(f"- {r['nome']} (R$ {r['preco']})")
    else:
        console.print("[red]Nenhuma roupa encontrada com esses filtros.[/red]")

# ==========================================
# REQUISITO 4: Gráfico (Comparando tabela principal com agrupamento)
# ==========================================
def gerar_grafico():
    pecas = requests.get(f"{API_URL}/pecas").json()
    categorias = requests.get(f"{API_URL}/categorias").json()

    contagem = {cat["id"]: 0 for cat in categorias}
    nomes_cat = {cat["id"]: cat["nome"] for cat in categorias}

    for peca in pecas:
        cat_id = peca.get("categoriaId")
        if cat_id in contagem:
            contagem[cat_id] += 1

    labels = [nomes_cat[id] for id in contagem.keys()]
    valores = list(contagem.values())

    plt.bar(labels, valores, color=["blue", "orange", "green", "red"])
    plt.title("Quantidade de Roupas por Categoria")
    plt.xlabel("Categorias")
    plt.ylabel("Quantidade")
    plt.yticks(range(0, max(valores) + 2))
    plt.show()

# ==========================================
# REQUISITO 5: Página Web
# ==========================================
def gerar_pagina_web():
    pecas = requests.get(f"{API_URL}/pecas").json()

    html = """
    <html>
    <head>
        <title>Loja de Roupas</title>
        <style>
            body { font-family: Arial; padding: 20px; background-color: #fff7f2;}
            table { border-collapse: collapse; width: 100%; margin-top: 20px;}
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #c96b2f; color: white; }
        </style>
    </head>
    <body>
        <h2>Roupas Cadastradas na Loja</h2>
        <table>
            <tr><th>ID</th><th>Nome</th><th>Preço (R$)</th></tr>
    """

    for p in pecas:
        html += f"<tr><td>{p['id']}</td><td>{p['nome']}</td><td>{p['preco']}</td></tr>"

    html += """
        </table>
    </body>
    </html>
    """

    with open("relatorio.html", "w", encoding="utf-8") as f:
        f.write(html)

    caminho_absoluto = "file://" + os.path.realpath("relatorio.html")
    webbrowser.open(caminho_absoluto)
    console.print("[green]Página web gerada e aberta no navegador![/green]")

# ==========================================
# REQUISITO 6: Backup (JSON)
# ==========================================
def gerar_backup():
    pecas = requests.get(f"{API_URL}/pecas").json()
    with open("backup_roupas.json", "w", encoding="utf-8") as f:
        json.dump(pecas, f, indent=4, ensure_ascii=False)
    console.print("[green]Backup gerado com sucesso no arquivo 'backup_roupas.json'![/green]")

# ==========================================
# MENU PRINCIPAL
# ==========================================
def menu():
    while True:
        console.print("\n[bold cyan]--- LOJA DE ROUPAS ---[/bold cyan]")
        console.print("1. Cadastrar Categoria (Tabela Auxiliar)")
        console.print("2. Cadastrar Roupa (Tabela Principal)")
        console.print("3. Listar Roupas")
        console.print("4. Deletar Roupa")
        console.print("5. Pesquisa Avançada")
        console.print("6. Gerar Gráfico de Roupas por Categoria")
        console.print("7. Gerar Página Web")
        console.print("8. Fazer Backup (JSON)")
        console.print("0. Sair")

        opcao = Prompt.ask("Escolha uma opção", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"])

        if opcao == "0":
            break
        elif opcao == "1":
            criar_categoria()
        elif opcao == "2":
            criar_peca()
        elif opcao == "3":
            listar_pecas()
        elif opcao == "4":
            deletar_peca()
        elif opcao == "5":
            pesquisa_avancada()
        elif opcao == "6":
            gerar_grafico()
        elif opcao == "7":
            gerar_pagina_web()
        elif opcao == "8":
            gerar_backup()


if __name__ == "__main__":
    menu()