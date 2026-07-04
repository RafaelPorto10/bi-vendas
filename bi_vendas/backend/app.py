import os
import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATA_PATH = os.path.join(os.path.dirname(__file__), "dados_comerciais.xlsx")


def carregar_dados():
    df = pd.read_excel(DATA_PATH)
    df.columns = df.columns.str.strip()
    df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce").fillna(0)
    df["Receita"] = pd.to_numeric(df["Receita"], errors="coerce").fillna(0)
    return df


@app.route("/api/resumo", methods=["GET"])
def resumo():
    df = carregar_dados()
    total_receita = round(df["Receita"].sum(), 2)
    total_itens = int(df["Quantidade"].sum())
    total_pedidos = len(df)
    ticket_medio = round(total_receita / total_pedidos, 2) if total_pedidos > 0 else 0

    return jsonify({
        "total_receita": total_receita,
        "total_itens": total_itens,
        "total_pedidos": total_pedidos,
        "ticket_medio": ticket_medio
    })


@app.route("/api/por-produto", methods=["GET"])
def por_produto():
    df = carregar_dados()
    agrupado = (
        df.groupby("Produto")
        .agg(quantidade=("Quantidade", "sum"), receita=("Receita", "sum"))
        .reset_index()
        .sort_values("receita", ascending=False)
    )
    agrupado["receita"] = agrupado["receita"].round(2)
    agrupado["quantidade"] = agrupado["quantidade"].astype(int)
    return jsonify(agrupado.to_dict(orient="records"))


@app.route("/api/por-localidade", methods=["GET"])
def por_localidade():
    df = carregar_dados()
    agrupado = (
        df.groupby("Localidade")
        .agg(quantidade=("Quantidade", "sum"), receita=("Receita", "sum"))
        .reset_index()
        .sort_values("receita", ascending=False)
    )
    agrupado["receita"] = agrupado["receita"].round(2)
    agrupado["quantidade"] = agrupado["quantidade"].astype(int)
    return jsonify(agrupado.to_dict(orient="records"))


@app.route("/api/por-mes", methods=["GET"])
def por_mes():
    df = carregar_dados()
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df["Mes"] = df["Data"].dt.to_period("M").astype(str)
    agrupado = (
        df.groupby("Mes")
        .agg(quantidade=("Quantidade", "sum"), receita=("Receita", "sum"))
        .reset_index()
        .sort_values("Mes")
    )
    agrupado["receita"] = agrupado["receita"].round(2)
    agrupado["quantidade"] = agrupado["quantidade"].astype(int)
    return jsonify(agrupado.to_dict(orient="records"))


@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({"status": "online", "versao": "1.0.0"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
