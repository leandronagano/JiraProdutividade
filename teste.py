from datetime import date, datetime

agora = datetime.now()

mes = agora.month
ano = agora.year

mesano = datetime(ano,mes,1).strftime("%B/%Y")

print(mesano)

mes = ""
ano = ""
mesano = ""