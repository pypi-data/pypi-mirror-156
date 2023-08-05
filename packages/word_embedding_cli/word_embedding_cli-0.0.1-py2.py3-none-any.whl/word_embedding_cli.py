"""
Word Embedding CLI.
"""

__version__ = '0.0.1'

from gensim.models import Word2Vec
import typer
import os
import re
import json as js
from typing import List

# dicaprio = x1
# actor = x2
# tarantino = y1


def analogy(x1, x2, y1, model):
    result = model.wv.most_similar(positive=[y1, x2], negative=[x1])
    return result[0][0]


def get_doesnt_match(words: list, model):
    return model.wv.doesnt_match(words)


def get_similar(word, size, model):
    return model.wv.most_similar(word, topn=size)


def get_most_similar(word, model):
    return model.wv.most_similar(word, topn=1)[0]


def load_model(path: str):
    if path == 'default':
        path = __file__
        path = re.sub(r'(\/[\w\d.\/]+\/.local\/).*',
                      r'\1wembcli_data/animals_300_50.model', path)
    return Word2Vec.load(path)


def calculator(words, model, negative_word=''):
    if negative_word != '':
        return model.wv.most_similar(positive=words, negative=[negative_word])[0][0]
    else:
        return model.wv.most_similar(positive=words)[0][0]


app = typer.Typer(help='Word Embeddings CLI')


@app.command('analogy', help='Retorna a relação de analogia entre duas palavras dado a relação de uma')
def cli_analogy(word1: str, relation1: str, word2: str, file_path: str = typer.Option('default', help='Path para um Modelo Word2Vec para ser carregado')):
    model = load_model(file_path)
    result_word1 = typer.style(word1, fg=typer.colors.GREEN, bold=True)
    result_relation1 = typer.style(relation1, fg=typer.colors.GREEN, bold=True)
    result_word2 = typer.style(word2, fg=typer.colors.YELLOW, bold=True)
    result_relation2 = typer.style(
        analogy(word1, relation1, word2, model), fg=typer.colors.YELLOW, bold=True)
    result = typer.style('\nANALOGY\n\n', underline=True, bold=True)
    result = result + result_word1 + ' is to ' + result_relation1 + \
        ' as ' + result_word2 + ' is to ' + result_relation2 + '\n'
    typer.echo(result)


@app.command('calculator', help='Calculadora de palavras')
def cli_calculator(words: List[str], negative_word: str = typer.Option(""), file_path: str = typer.Option('default', help='Path para um Modelo Word2Vec para ser carregado')):
    model = load_model(file_path)
    words = list(words)
    result_calculator = calculator(words, model, negative_word)
    result = typer.style('\nCALCULATOR\n\n',
                         underline=True, bold=True)
    if negative_word == '':
        for i in range(len(words)):
            if (i == len(words) - 1):
                sum_word = typer.style(words[i], fg=typer.colors.YELLOW)
                operation = typer.style(' = ', bold=True)
                result_calculator = typer.style(
                    result_calculator, fg=typer.colors.GREEN, bold=True, underline=True)
                result = result + sum_word + operation + result_calculator + '\n'
            else:
                sum_word = typer.style(words[i], fg=typer.colors.YELLOW)
                operation = typer.style(' + ', bold=True)
                result = result + sum_word + operation
    else:
        for i in range(len(words)):
            if (i == len(words) - 1):
                sum_word = typer.style(words[i], fg=typer.colors.YELLOW)
                operation = typer.style(' - ', bold=True)
                result = result + sum_word + operation
            else:
                sum_word = typer.style(words[i], fg=typer.colors.YELLOW)
                operation = typer.style(' + ', bold=True)
                result = result + sum_word + operation
        sub_word = typer.style(negative_word, fg=typer.colors.RED, bold=True)
        operation = typer.style(' = ', bold=True)
        result_calculator = typer.style(
            result_calculator, fg=typer.colors.GREEN, bold=True, underline=True)
        result = result + sub_word + operation + result_calculator + '\n'
    typer.echo(result)


@app.command('differ', help='Retorna a palavra que não pertence à lista')
def cli_doesnt_match(words: List[str], file_path: str = typer.Option('default', help='Path para um Modelo Word2Vec para ser carregado')):
    model = load_model(file_path)
    words = list(words)
    result = typer.style('\nDOESN\'T MATCH\n\n',
                         underline=True, bold=True)
    result_discordant = get_doesnt_match(words, model)
    words.remove(result_discordant)
    result_word = ''
    for word in words:
        result_word = result_word + word + ', '
    result_word = result_word[:-2]
    result_discordant = typer.style(
        result_discordant, fg=typer.colors.BRIGHT_RED, bold=True, underline=True)
    result_word = typer.style(result_word, fg=typer.colors.GREEN, bold=True)
    result = result + result_discordant + \
        ' doesn\'t match with ' + result_word + '\n'
    typer.echo(result)


@app.command('most-similar', help='Retorna a palavra mais semelhante à fornecida')
def cli_most_similar(word: str, file_path: str = typer.Option('default', help='Path para um Modelo Word2Vec para ser carregado')):
    model = load_model(file_path)
    result_similar = get_most_similar(word, model)
    result = typer.style('\nMOST SIMILAR\n\n',
                         underline=True, bold=True)
    results_word = typer.style(
        result_similar[0], fg=typer.colors.GREEN, bold=True)
    result_degree = typer.style(str(result_similar[1]))
    result = result + results_word + ': ' + result_degree + '\n'
    typer.echo(result)


@app.command('similar', help='Retorna as palavras semelhantes à fornecida, sendo possível retornar o número de palavras variável')
def cli_similar(word: str, json: bool = False, save: bool = False, size: int = typer.Option(10, help='Número de resultados apresentados'), file_path: str = typer.Option('default', help='Path para um Modelo Word2Vec para ser carregado')):
    model = load_model(file_path)
    results = get_similar(word, size, model)
    if not json:
        result = typer.style('\nSIMILAR\n\nResults\n',
                             underline=True, bold=True)
        for result_tuple in results:
            results_word = typer.style(
                result_tuple[0], fg=typer.colors.GREEN, bold=True)
            result_degree = typer.style(str(result_tuple[1]))
            result = result + results_word + ': ' + result_degree + '\n'
        typer.echo(result)
    else:
        result = typer.style('\nSIMILAR\n\nJSON\n',
                             underline=True, bold=True)
        json_list = list()
        for result_tuple in results:
            json_list.append(
                {'word': result_tuple[0], 'degree': result_tuple[1]})
        json_str = js.dumps(json_list, indent=2, ensure_ascii=False)
        if not save:
            result = result + json_str
            typer.echo(result)
        else:
            file_name = typer.prompt("File name to save JSON")
            with open(file_name+'.json', 'w+') as f:
                f.write(json_str)
                typer.echo(result)
                typer.secho(
                    f'Results saved on {file_name}.json!\n', fg=typer.colors.GREEN)


def __main__():
    app()
