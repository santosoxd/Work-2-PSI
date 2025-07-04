import sys
import tkinter as tk
from tkinter import messagebox, simpledialog

sys.path.append('C:/Users/l2457/Desktop/Breno/')

from connect_db import start_connection

def adicionar_filme_sessao(titulo, duracao, classificacao, sessoes_info):
    conn = start_connection()
    if conn is None:
        return False, "Falha na conexão com o banco de dados."

    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO filmes (titulo, duracao, classificacao) VALUES (%s, %s, %s)", (titulo, duracao, classificacao)
        )
        filme_id = cursor.lastrowid

        for horario, assentos in sessoes_info:
            cursor.execute(
                "INSERT INTO sessoes (filme_id, horario, assentos_disponiveis) VALUES (%s, %s, %s)", (filme_id, horario, assentos)
            )

        conn.commit()
        return True, "Sessão(ões) adicionada(s) com sucesso."
    except ValueError as e:
        conn.rollback()
        return False, f"Erro ao adicionar sessão: {e}"


def listar_sessoes():
    conn = start_connection()
    if conn is None:
        return []

    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT sessoes.id AS sessao_id, filmes.titulo, filmes.duracao, filmes.classificacao, sessoes.horario, sessoes.assentos_disponiveis
        FROM sessoes
        JOIN filmes ON sessoes.filme_id = filmes.id
        """
        cursor.execute(query)
        sessoes = cursor.fetchall()
        return sessoes
    except ValueError:
        return []

def remover_sessao(sessao_id):
    conn = start_connection()
    if conn is None:
        return False

    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM sessoes WHERE id = %s", (sessao_id,))
        conn.commit()
        return cursor.rowcount > 0
    except ValueError:
        conn.rollback()
        return False


def comprar_ingresso(nome, nif, sessao_id, quantidade):
    conn = start_connection()
    if conn is None:
        return False, "Falha na conexão com o banco."

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT assentos_disponiveis FROM sessoes WHERE id = %s", (sessao_id,))
        resultado = cursor.fetchone()
        if resultado is None:
            return False, "Sessão não encontrada."
        assentos_disponiveis = resultado[0]
        if assentos_disponiveis < quantidade:
            return False, "Assentos insuficientes."

        cursor.execute("SELECT id FROM clientes WHERE NIF = %s", (nif,))
        cliente = cursor.fetchone()

        if cliente is None:
            cursor.execute("INSERT INTO clientes (nome, nif) VALUES (%s, %s)", (nome, nif))
            cliente_id = cursor.lastrowid
        else:
            cliente_id = cliente[0]

        cursor.execute(
            "UPDATE sessoes SET assentos_disponiveis = assentos_disponiveis - %s WHERE id = %s", (quantidade, sessao_id)
        )

        for _ in range(quantidade):
            cursor.execute("INSERT INTO ingressos (cliente_id, sessao_id) VALUES (%s, %s)", (cliente_id, sessao_id))

        conn.commit()
        return True, f"{quantidade} ingresso(s) comprado(s) com sucesso."
    except ValueError as e:
        conn.rollback()
        return False, f"Erro ao comprar ingresso: {e}"

def bilhetes_cliente(nif):
    conn = start_connection()
    if conn is None:
        return []

    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT filmes.titulo, sessoes.horario
        FROM ingressos
        JOIN clientes ON ingressos.cliente_id = clientes.id
        JOIN sessoes ON ingressos.sessao_id = sessoes.id
        JOIN filmes ON sessoes.filme_id = filmes.id
        WHERE clientes.NIF = %s
        """
        cursor.execute(query, (nif,))
        resultados = cursor.fetchall()
        bilhetes = [f"{row['titulo']} às {row['horario']}" for row in resultados]
        return bilhetes
    except ValueError:
        return []



# --- Interface Tkinter ---
class SistemaCinemaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Cinema")
        self.geometry("400x400")

        tk.Button(self, text="Adicionar Filmes", command=self.adicionar_sessao).pack(pady=10)
        tk.Button(self, text="Listar Filmes", command=self.listar_sessoes_gui).pack(pady=10)
        tk.Button(self, text="Remover Sessão", command=self.remover_sessao_gui).pack(pady=10)
        tk.Button(self, text="Comprar Ingresso", command=self.comprar_ingresso_gui).pack(pady=10)
        tk.Button(self, text="Mostrar Bilhetes", command=self.mostrar_bilhetes_gui).pack(pady=10)

    def adicionar_sessao(self):
        try:
            titulo = simpledialog.askstring("Filme", "Título do Filme:")
            if not titulo:
                raise ValueError("Título não pode ser vazio.")

            duracao = simpledialog.askinteger("Filme", "Duração (minutos):")
            if duracao is None or duracao <= 0:
                raise ValueError("Duração inválida.")

            classificacao = simpledialog.askstring("Filme", "Classificação (ex: M/12):")
            if not classificacao:
                raise ValueError("Classificação não pode ser vazia.")

            sessoes_info = []
            while True:
                horario = simpledialog.askstring("Sessão", "Horário da Sessão (ex: 21:00):")
                if not horario:
                    raise ValueError("Horário não pode ser vazio.")

                assentos = simpledialog.askinteger("Sessão", "Número de Assentos Disponíveis:")
                if assentos is None or assentos <= 0:
                    raise ValueError("Número de assentos inválido.")

                sessoes_info.append((horario, assentos))

                continuar = messagebox.askyesno("Adicionar mais sessões?", "Deseja adicionar outra sessão para esse filme?")
                if not continuar:
                    break

            sucesso, msg = adicionar_filme_sessao(titulo, duracao, classificacao, sessoes_info)
            if sucesso:
                messagebox.showinfo("Sucesso", msg)
            else:
                messagebox.showerror("Erro", msg)

        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def listar_sessoes_gui(self):
        sessoes = listar_sessoes()
        if not sessoes:
            messagebox.showinfo("Sessões", "Nenhuma sessão cadastrada ou erro ao buscar.")
            return

        texto = ""
        for sessao in sessoes:
            texto += (f"ID: {sessao['sessao_id']} - Filme: {sessao['titulo']} - Horário: {sessao['horario']} - "
                      f"Duração: {sessao['duracao']} min - Classificação: {sessao['classificacao']} - "
                      f"Assentos Disponíveis: {sessao['assentos_disponiveis']}\n")
        self.mostrar_texto_em_janela("Sessões", texto)

    def remover_sessao_gui(self):
        try:
            sessao_id = simpledialog.askinteger("Remover Sessão", "Informe o ID da sessão a remover:")
            if sessao_id is None:
                return
            if remover_sessao(sessao_id):
                messagebox.showinfo("Sucesso", "Sessão removida com sucesso.")
            else:
                messagebox.showerror("Erro", "Sessão não encontrada ou erro ao remover.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def comprar_ingresso_gui(self):
        try:
            nome = simpledialog.askstring("Cliente", "Nome do Cliente:")
            if not nome:
                raise ValueError("Nome não pode ser vazio.")

            nif = simpledialog.askstring("Cliente", "NIF do Cliente:")
            if not nif:
                raise ValueError("NIF não pode ser vazio.")

            sessoes = listar_sessoes()
            if not sessoes:
                messagebox.showinfo("Info", "Não há sessões disponíveis.")
                return

            texto = ""
            for sessao in sessoes:
                texto += (f"ID: {sessao['sessao_id']} - Filme: {sessao['titulo']} - Horário: {sessao['horario']} - "
                          f"Assentos: {sessao['assentos_disponiveis']}\n")
            self.mostrar_texto_em_janela("Sessões disponíveis", texto)

            sessao_id = simpledialog.askinteger("Compra", "Informe o ID da sessão para comprar ingresso:")
            if sessao_id is None:
                return

            quantidade = simpledialog.askinteger("Compra", "Quantidade de ingressos:")
            if quantidade is None or quantidade <= 0:
                raise ValueError("Quantidade inválida.")

            sucesso, msg = comprar_ingresso(nome, nif, sessao_id, quantidade)
            if sucesso:
                messagebox.showinfo("Sucesso", msg)
            else:
                messagebox.showerror("Erro", msg)
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def mostrar_bilhetes_gui(self):
        nif = simpledialog.askstring("Bilhetes", "Informe o NIF do cliente:")
        if not nif:
            messagebox.showerror("Erro", "NIF não pode ser vazio.")
            return

        bilhetes = bilhetes_cliente(nif)
        if not bilhetes:
            messagebox.showinfo("Bilhetes", "Nenhum bilhete encontrado para este NIF.")
        else:
            texto = "\n".join(bilhetes)
            self.mostrar_texto_em_janela("Bilhetes do Cliente", texto)

    def mostrar_texto_em_janela(self, titulo, texto):
        janela = tk.Toplevel(self)
        janela.title(titulo)
        txt = tk.Text(janela, wrap=tk.WORD, width=120, height=20)
        txt.insert(tk.END, texto)
        txt.config(state=tk.DISABLED)
        txt.pack(padx=10, pady=10)

if __name__ == "__main__":
    app = SistemaCinemaApp()
    app.mainloop()
