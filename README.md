<img align="left" width="500" height="500" src="https://github.com/renato-evangelista/house-rocket/blob/main/img1.png">

## Introdução

House Rocket é uma empresa fictícia do mercado imobiliário - seu modelo de negócio envolve comprar e revender imóveis. Porém, o time de negócios enfrenta um mercado com diversas variáveis que influenciam o preço - a quantidade de dados é grande e levaria muito tempo para fazer o trabalho manualmente.

Portanto, esse projeto tem o objetivo de gerar insights através da análise e manipulação dos dados para auxiliar na tomada de decisão do time de negócios.

## Produto Final

Com o objetivo de encontrar quais imóveis a House Rocket deveria comprar e, uma vez comprados, em qual momento deveria vendê-los e por qual preço, serão entregues os seguintes produtos:

* Relatório com as sugestões de compra do imóvel com um valor recomendado;

* Relatório com as sugestões de venda do imóvel com um valor recomendado e o melhor momento para a venda;

* App com os dados de cada imóvel indicado nos relatórios.

## Dados

A base de dados corresponde a imóveis vendidos na região de King County, Seattle, entre 2014 e 2015. Todas as informações estão disponíveis no Kaggle¹:

| Coluna        | Descrição                                                             |
|---------------|-----------------------------------------------------------------------|
| id            | Identificação do imóvel a cada venda                                  |
| date          | Data da venda                                                         |
| price         | Preço do imóvel                                                       |
| bedrooms      | Quantidade de quartos                                                 |
| bathrooms     | Quantidade de banheiros (0,5 corresponde a um banheiro sem chuveiro ) |
| sqft_living   | Área interna do imóvel                                                |
| sqft_lot      | Área do lote/terreno                                                  |
| floors        | Quantidade de andares                                                 |
| waterfront    | Indicador de vista para o lago da cidade                              |
| view          | Indicador de 0 a 4 avaliando a vista do imóvel                        |
| condition     | Indicador de 0 a 5 avaliando o estado do imóvel                       |
| grade         | Indicador de 1 a 13 avaliando o design e construção do imóvel         |
| sqft_above    | Área acima do nível do solo                                           |
| sqft_basement | Área abaixo do nível do solo                                          |
| yr_built      | Ano de construção do imóvel                                           |
| yr_renovated  | Ano da última reforma do imóvel                                       |
| zipcode       | Equivalente ao CEP                                                    |
| lat           | Latitude                                                              |
| long          | Longitude                                                             |

## Premissas

* As features sqft_living15 e sqft_lot15, que correspondem a área dos imóveis vizinhos, foram desconsideradas;
* Imóveis com ano de renovação igual a 0 foram considerados sem reforma;
* Para os id’s repetidos, foi considerada a venda mais recente do imóvel;
* A linha correspondente a um imóvel com 33 quartos foi removida por ser considerada um erro de digitação.

## Ferramentas

* Python 3.10

* Google Colab

* PyCharm

* Streamlit

* Heroku

## Desenvolvimento da Solução

A solução foi dividida em duas etapas: a etapa de compra e a etapa de venda do imóvel. Além disso, considerei como premissa do negócio a sazonalidade de vendas desse segmento de mercado imobiliário.

Para a compra, com os dados tratados e organizados, durante a análise exploratória levantei algumas hipóteses - que serão abordadas no item “Insights”. As hipóteses mais relevantes, como a que se referia à condição do imóvel, foram levadas em consideração para a compra do mesmo.

Para a venda, agrupei os imóveis por região (zipcode) e por sazonalidade (estação do ano) e retornei a mediana do preço. Imóveis com valor acima do valor mediano da região serão vendidos com acréscimo de 10%. Imóveis com valor abaixo do valor mediano da região serão vendidos com acréscimo de 30%. Sendo assim, considerei a melhor época do ano para venda em cada região.



## Insights

* Imóveis com vista para a água são, em média, 212% mais caros do que imóveis sem vista para a água;

* Imóveis com porão são, em média, 28% mais caros do que imóveis sem porão;

* Imóveis térreos são, em média, 30% mais baratos do que imóveis com andar;

* Imóveis com até 2 quartos são, em média, 30% mais baratos do que imóveis com mais quartos;

* Imóveis com até 1 banheiro são, em média, 40% mais baratos do que imóveis com mais banheiros.

## Resultados Financeiros

Considerando todos os insights descritos anteriormente, identifiquei 429 oportunidades de compra. Essas oportunidades, somadas, geram um lucro de aproximadamente 40 milhões de dólares - o lucro médio, por imóvel, é de 93 mil dólares.

## Conclusão e Próximos Passos

É evidente que ao considerar os insights, encontramos boas oportunidades de compra e venda para a House Rocket. Os imóveis identificados para a compra foram os mais baratos e em boas condições, seguindo o modelo de negócio da empresa.

De um lado, a quantidade de casas compradas é maior - amplia-se a variedade para os clientes. De outro, perde-se oportunidades de negócio - como, por exemplo, casas em condições regulares em ótima localização que possibilitam lucrar com a reforma.

Portanto, como próximo passo, aplicaria ferramentas da Ciência de Dados como algoritmos de regressão (machine learning) e realizaria pesquisa de mercado para identificar as principais features consideradas pelos clientes.

## Anexos

https://www.kaggle.com/datasets/harlfoxem/housesalesprediction
