from flask import Flask, jsonify, send_from_directory
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)

# Informations de connexion à la base de données
server = 'DESKTOP-VM6ODM7'
database = 'PI_Foot'
username = '' 
password = ''  

# Chaîne de connexion SQLAlchemy
conn_str = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'

# Créer un moteur SQLAlchemy
engine = create_engine(conn_str)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_angular(path):
    return send_from_directory('Frontend/dist/frontend', 'index.html')

# Autres routes pour les fichiers statiques et l'API
@app.route('/app/<path:path>')
def serve_static(path):
    return send_from_directory('Frontend/dist/frontend', path)

@app.route('/api/data')
def get_data():
    # Votre fonction pour obtenir des données depuis le backend Flask
    data = {'message': 'Ceci est un exemple de données provenant du backend Flask.'}
    return jsonify(data)

@app.route('/')
def index():
    try:
        # Limiter la quantité de données en utilisant une requête SQL optimisée
        sql_query = """
        SELECT * FROM Fact_performance_Indiv 
        WHERE FK_Team IN (SELECT TOP 100 FK_Team FROM Fact_performance_Indiv ORDER BY FK_Team DESC)
        """
        # Lire les données dans un DataFrame pandas en utilisant le moteur SQLAlchemy
        df = pd.read_sql(sql_query, engine)

        # Supprimer les lignes en double
        df = df.drop_duplicates()

        # Calculer la matrice de corrélation de manière incrémentielle
        correlation_matrix = pd.DataFrame()
        chunk_size = 50
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i+chunk_size]
            correlation_matrix = pd.concat([correlation_matrix, chunk.corr()])

        # Filtrer les paires de colonnes ayant une forte corrélation
        strong_correlation_threshold = 0.7
        strong_correlations = correlation_matrix[(correlation_matrix.abs() > strong_correlation_threshold) & (correlation_matrix.abs() < 1.0)]
        strong_correlations = strong_correlations.unstack().sort_values(ascending=False).drop_duplicates()

        # Formatage des paires de colonnes avec une forte corrélation
        strong_correlation_list = []
        for pair, correlation in strong_correlations.items():
            if not pd.isnull(correlation):
                strong_correlation_list.append({
                    'pair': pair,
                    'correlation': correlation
                })

        # Retourner les paires de colonnes avec une forte corrélation au format JSON
        return jsonify(strong_correlations=strong_correlation_list)

    except Exception as e:
        return f"Une erreur s'est produite : {e}"

if __name__ == '__main__':
    app.run(debug=True)
