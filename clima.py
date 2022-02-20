import argparse
import json
import sys
from configparser import ConfigParser
from urllib import error, parse, request

import estilo

URL_BASE = "https://api.openweathermap.org/data/2.5/weather"

TEMPESTADE = range(200, 300)
GAROA = range(300, 400)
CHUVA = range(500, 600)
NEVE = range(600, 700)
ATMOSFERA = range(700, 800)
CLARO = range(800, 801)
NUBLADO = range(801, 900)


def get_api_key():
    config = ConfigParser()
    config.read("./API_KEY/secrets.ini")
    return config["openweather"]["api_key"]


def read_user_cli_args():
    parser = argparse.ArgumentParser(
        description="Informação de clima e temperatura por cidade"
    )
    parser.add_argument("cidade", nargs="+", help="Entre com nome da cidade")
    parser.add_argument(
        "-i",
        "--imperial",
        action="store_true",
        help="Mostra temperatura em medidas imperiais",
    )
    return parser.parse_args()


def busca_clima(cidade, imperial=False):
    api_key = get_api_key()
    nome_cidade = " ".join(cidade)
    nome_cidade_enc = parse.quote_plus(nome_cidade)
    unidades = "imperial" if imperial else "metric"
    url = (
        f"{URL_BASE}?q={nome_cidade_enc}"
        f"&units={unidades}&appid={api_key}&lang=pt_br"
    )
    return url


def get_dados_clima(query_url):
    try:
        r = request.urlopen(query_url)
    except error.HTTPError as http_error:
        if http_error.code == 401:
            sys.exit("Acesso negado. Verifique sua chave de API")
        elif http_error.code == 404:
            sys.exit("Não foi encontrado dados para essa cidade.")
        else:
            sys.exit(f"Algo errado...({http_error.code})")

    data = r.read()

    try:
        return json.loads(data)
    except json.JSONDecoderError:
        sys.exit("Não foi possível ler o arquivo do servidor.")


def info_clima(dados_clima, imperial=False):
    cidade = dados_clima["name"]
    pais = dados_clima["sys"]["country"]
    clima_id = dados_clima["weather"][0]["id"]
    desc_clima = dados_clima["weather"][0]["description"]
    temperatura = dados_clima["main"]["temp"]
    vento = dados_clima["wind"]["speed"]

    estilo.muda_cor(estilo.INVERTE_FUNDO)
    print(f"{cidade}, {pais} ", end="")
    estilo.muda_cor(estilo.RESET)

    simbolo, cor = seleciona_cor_clima(clima_id)

    estilo.muda_cor(cor)
    print(f"\t{simbolo}", end=" ")
    print(f"\t{desc_clima.capitalize():^{estilo.ESPACO}}", end=" ")
    estilo.muda_cor(estilo.RESET)

    print(
        f"(🌡️ {round(temperatura,1)}°"
        f"{'F' if imperial else 'C'})", end=" "
    )
    print(
        f"(💨 {round(vento, 1) if imperial else round(vento * 3.6, 1)}"
        f"{'mph' if imperial else 'km/h'})"
    )


def seleciona_cor_clima(clima_id):
    if clima_id in TEMPESTADE:
        return "💥", estilo.VERMELHO
    elif clima_id in GAROA:
        return "💧", estilo.CIANO
    elif clima_id in CHUVA:
        return "💦", estilo.AZUL
    elif clima_id in NEVE:
        return "⛄️", estilo.BRANCO
    elif clima_id in ATMOSFERA:
        return "🌀", estilo.AZUL
    elif clima_id in CLARO:
        return "🔆", estilo.AMARELO
    elif clima_id in NUBLADO:
        return "🌁", estilo.BRANCO
    else:
        return "🌈", estilo.RESET


if __name__ == "__main__":
    user_args = read_user_cli_args()
    query_url = busca_clima(user_args.cidade, user_args.imperial)
    dados_clima = get_dados_clima(query_url)
    info_clima(dados_clima, user_args.imperial)
