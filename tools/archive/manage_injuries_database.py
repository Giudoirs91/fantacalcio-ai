import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import json
import unicodedata
import pandas as pd
from bs4 import BeautifulSoup

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_DIR, "config", "infortuni_storici_2025_26.json")

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.stats_processor import load_quotazioni

def norm(text):
    if not text: return ""
    cleaned = ''.join(c for c in unicodedata.normalize('NFD', str(text).replace('ı', 'i').replace('İ', 'i').replace('Ø', 'O').replace('ø', 'o')) if unicodedata.category(c) != 'Mn').lower()
    return cleaned.replace(' ', '').replace('.', '').replace('-', '').replace("'", '')

def init_full_database():
    df = load_quotazioni()
    db = {}
    for _, row in df.iterrows():
        team = str(row.get('Squadra', '')).strip()
        pname = str(row.get('Nome', '')).strip()
        role = str(row.get('R', '')).strip().upper()
        fvm = float(row.get('FVM', 1.0))
        
        if team not in db:
            db[team] = {}
            
        db[team][pname] = {
            "id": int(row.get('Id', 0)),
            "ruolo": role,
            "fvm": fvm,
            "in_rosa_2627": True,
            "squadra_2627": team,
            "tm_matched_name": None,
            "partite_saltate": 0,
            "giornate_saltate": [],
            "diagnosi": [],
            "livello_fragilita": "🟢 Bassa"
        }
    return db

def load_or_init_db():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                db = json.load(f)
                if db and len(db) > 0:
                    return db
        except Exception:
            pass
    return init_full_database()

def parse_transfermarkt_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    if len(tables) < 2:
        return {}
    
    table = tables[1]
    rows = table.find_all('tr')
    tm_players = {}

    for r in rows[1:]:
        tds = r.find_all('td')
        if len(tds) > 2:
            name = tds[1].get_text(strip=True)
            pos = tds[2].get_text(strip=True)
            
            match_tds = [td for td in tds[3:] if 'afz' in td.get('class', [])]
            if not match_tds: match_tds = tds[4::2]
            
            real_injuries = []
            for g_idx, td in enumerate(match_tds):
                giornata = g_idx + 1
                span_v = td.find('span', class_='verletzt-table')
                if span_v:
                    title = span_v.get('title', '').strip()
                    diag = title.split(' - ')[0] if ' - ' in title else title
                    real_injuries.append((giornata, diag))
                    
            tm_players[name] = {
                'pos': pos,
                'injuries_count': len(real_injuries),
                'injuries': real_injuries
            }
    return tm_players

def match_tm_player_to_listone(tm_name, tm_data, listone_players):
    """
    Trova la corrispondenza migliore nel listone completo 2026/27 per un giocatore di Transfermarkt.
    """
    norm_tm = norm(tm_name)
    pos_tm = tm_data['pos'].upper()

    # Mappe e disambiguazioni specifiche
    raw_explicit_map = {
        "david neres": ("Neres", "Napoli"),
        "kevin de bruyne": ("De Bruyne", "Napoli"),
        "frank anguissa": ("Zambo Anguissa", "Napoli"),
        "amir rrahmani": ("Rrahmani", "Napoli"),
        "billy gilmour": ("Gilmour", "Napoli"),
        "alex meret": ("Meret", "Napoli"),
        "giovanni di lorenzo": ("Di Lorenzo", "Napoli"),
        "antonio vergara": ("Vergara", "Napoli"),
        "nikita contini": ("Contini", "Napoli"),
        "stanislav lobotka": ("Lobotka", "Napoli"),
        "scott mctominay": ("McTominay", "Napoli"),
        "leonardo spinazzola": ("Spinazzola", "Napoli"),
        "pasquale mazzocchi": ("Mazzocchi", "Napoli"),
        "alessandro buongiorno": ("Buongiorno", "Napoli"),
        "sam beukema": ("Beukema", "Napoli"),
        "mathias olivera": ("Olivera", "Napoli"),
        "matteo politano": ("Politano", "Napoli"),
        "rasmus hojlund": ("Hojlund", "Napoli"),
        "vanja milinkovic-savic": ("Milinkovic-Savic V.", "Napoli"),
        "vanja milinkovicsavic": ("Milinkovic-Savic V.", "Napoli"),
        "lorenzo lucca": ("Lucca", "Napoli"),
        "alisson santos": ("Santos A.", "Napoli"),
        "noa lang": ("Lang", "Napoli"),
        "giovane": ("Giovane", "Napoli"),
        "luca marianucci": ("Marianucci", "Napoli"),

        "hakan calhanoglu": ("Calhanoglu", "Inter"),
        "marcus thuram": ("Thuram", "Inter"),
        "henrikh mkhitaryan": ("Mkhitaryan", "Inter"),
        "lautaro martinez": ("Martinez L.", "Inter"),
        "josep martinez": ("Martinez Jo.", "Inter"),
        "yann bisseck": ("Bisseck", "Inter"),
        "ange-yoan bonny": ("Bonny", "Inter"),
        "angeyoan bonny": ("Bonny", "Inter"),
        "alessandro bastoni": ("Bastoni", "Inter"),
        "nicolo barella": ("Barella", "Inter"),
        "andy diouf": ("Diouf", "Inter"),
        "carlos augusto": ("Carlos Augusto", "Inter"),
        "luis henrique": ("Luis Henrique", "Inter"),
        "pio esposito": ("Esposito F.P.", "Inter"),
        "raffaele di gennaro": ("Di Gennaro", "Inter"),
        "federico dimarco": ("Dimarco", "Inter"),
        "benjamin pavard": ("Pavard", "Inter"),
        "manuel akanji": ("Akanji", "Inter"),
        "piotr zielinski": ("Zielinski", "Inter"),
        "petar sucic": ("Sucic P.", "Inter"),

        "paulo dybala": ("Dybala", "Roma"),
        "lorenzo pellegrini": ("Pellegrini Lo.", "Roma"),
        "manu kone": ("Konè M.", "Roma"),
        "mario hermoso": ("Hermoso", "Roma"),
        "wesley": ("Wesley", "Roma"),
        "matias soule": ("Soulè", "Roma"),
        "pierluigi gollini": ("Gollini", "Roma"),
        "devyne rensch": ("Rensch", "Roma"),
        "gianluca mancini": ("Mancini", "Roma"),
        "evan ndicka": ("N'Dicka", "Roma"),
        "robinio vaz": ("Vaz", "Roma"),
        "mile svilar": ("Svilar", "Roma"),
        "giorgio de marzi": ("De Marzi", "Roma"),
        "daniele ghilardi": ("Ghilardi", "Roma"),
        "jan ziolkowski": ("Ziolkowski", "Roma"),
        "emanuele lulli": ("Lulli", "Roma"),
        "bryan cristante": ("Cristante", "Roma"),
        "niccolo pisilli": ("Pisilli", "Roma"),
        "neil el aynaoui": ("El Aynaoui", "Roma"),
        "donyell malen": ("Malen", "Roma"),
        "santiago castro": ("Castro S.", "Roma"),

        "santiago gimenez": ("Gimenez", "Milan"),
        "ardon jashari": ("Jashari", "Milan"),
        "christian pulisic": ("Pulisic", "Milan"),
        "matteo gabbia": ("Gabbia", "Milan"),
        "ruben loftus-cheek": ("Loftus-Cheek", "Milan"),
        "ruben loftuscheek": ("Loftus-Cheek", "Milan"),
        "adrien rabiot": ("Rabiot", "Milan"),
        "pervis estupinan": ("Estupinan", "Milan"),
        "lorenzo torriani": ("Torriani", "Milan"),
        "luka modric": ("Modric", "Milan"),
        "alexis saelemaekers": ("Saelemaekers", "Milan"),
        "youssouf fofana": ("Fofana Y.", "Milan"),
        "mike maignan": ("Maignan", "Milan"),
        "strahinja pavlovic": ("Pavlovic", "Milan"),
        "pietro terracciano": ("Terracciano", "Milan"),
        "davide bartesaghi": ("Bartesaghi", "Milan"),
        "fikayo tomori": ("Tomori", "Milan"),
        "koni de winter": ("De Winter", "Milan"),
        "samuel chukwueze": ("Chukwueze", "Milan"),
        "yunus musah": ("Musah", "Milan"),

        "arkadiusz milik": ("Milik", "Juventus"),
        "juan cabal": ("Cabal", "Juventus"),
        "carlo pinsoglio": ("Pinsoglio", "Juventus"),
        "bremer": ("Bremer", "Juventus"),
        "daniele rugani": ("Rugani", "Juventus"),
        "federico gatti": ("Gatti", "Juventus"),
        "francisco conceicao": ("Conceicao", "Juventus"),
        "lloyd kelly": ("Kelly L.", "Juventus"),
        "khephren thuram": ("Thuram K.", "Juventus"),
        "edon zhegrova": ("Zhegrova", "Juventus"),
        "kenan yildiz": ("Yildiz", "Juventus"),
        "pierre kalulu": ("Kalulu", "Juventus"),
        "andrea cambiaso": ("Cambiaso", "Juventus"),
        "manuel locatelli": ("Locatelli", "Juventus"),
        "teun koopmeiners": ("Koopmeiners", "Juventus"),
        "weston mckennie": ("McKennie", "Juventus"),
        "nico gonzalez": ("Gonzalez N.", "Juventus"),
        "jonathan david": ("David", "Juventus"),
        "jeremie boga": ("Boga", "Juventus"),
        "jhon lucumi": ("Lucumì", "Juventus"),

        "jayden addai": ("Addai", "Como"),
        "assane diao": ("Diao", "Como"),
        "edoardo goldaniga": ("Goldaniga", "Como"),
        "ignace van der brempt": ("Van Der Brempt", "Como"),
        "adrian lahdo": ("Lahdo", "Como"),
        "jacobo ramon": ("Ramon", "Como"),
        "alex valle": ("Valle", "Como"),
        "nico paz": ("Paz N.", "Como"),
        "martin baturina": ("Baturina", "Como"),
        "jesus rodriguez": ("Rodriguez Je.", "Como"),
        "jean图标": ("Butez", "Como"),
        "jean butez": ("Butez", "Como"),
        "noel tornqvist": ("Tornqvist", "Como"),
        "mauro vigorito": ("Vigorito", "Como"),
        "marc oliver kempf": ("Kempf", "Como"),
        "ivan smolcic": ("Smolcic I.", "Como"),
        "lucas da cunha": ("Da Cunha", "Como"),
        "maximo perrone": ("Perrone", "Como"),
        "maxence caqueret": ("Caqueret", "Como"),
        "anastasios douvikas": ("Douvikas", "Como"),
        "nicolas kuhn": ("Kuhn", "Como"),
        "ivan azon": ("Azon", "Como"),
        "stefan posch": ("Posch", "Como"),

        # Milan
        "mike maignan": ("Maignan", "Milan"),
        "pietro terracciano": ("Terracciano", "Milan"),
        "lorenzo torriani": ("Torriani", "Milan"),
        "strahinja pavlovic": ("Pavlovic", "Milan"),
        "matteo gabbia": ("Gabbia", "Milan"),
        "pervis estupinan": ("Estupinan", "Milan"),
        "koni de winter": ("De Winter", "Milan"),
        "fikayo tomori": ("Tomori", "Milan"),
        "davide bartesaghi": ("Bartesaghi", "Milan"),
        "ardon jashari": ("Jashari", "Milan"),
        "youssouf fofana": ("Fofana Y.", "Milan"),
        "adrien rabiot": ("Rabiot", "Milan"),
        "ruben loftus-cheek": ("Loftus-Cheek", "Milan"),
        "ruben loftuscheek": ("Loftus-Cheek", "Milan"),
        "luka modric": ("Modric", "Milan"),
        "alexis saelemaekers": ("Saelemaekers", "Milan"),
        "christian pulisic": ("Pulisic", "Milan"),
        "samuel chukwueze": ("Chukwueze", "Milan"),
        "yunus musah": ("Musah", "Milan"),
        "santiago gimenez": ("Gimenez", "Milan"),
        "filippo terracciano": ("Terracciano F.", "Milan"),
        "samuele ricci": ("Ricci S.", "Como"),
        "alex jimenez": ("Jimenez A.", "Fiorentina"),

        # Torino
        "che adams": ("Adams C.", "Torino"),
        "duvan zapata": ("Zapata D.", "Torino"),

        # Parma
        "mandela keita": ("Keita M.", "Parma"),

        # Cagliari
        "juan rodriguez": ("Rodriguez Ju.", "Cagliari"),
        "ze pedro": ("Zè Pedro", "Cagliari"),
        "riyad idrissi": ("Idrissi R.", "Cagliari"),

        # Venezia
        "bartol franjic": ("Franjic", "Venezia"),
        "john yeboah": ("Yeboah J.", "Venezia"),
        "gianluca busio": ("Busio", "Venezia"),
        "toma basic": ("Basic", "Venezia"),
        "simon sohm": ("Sohm", "Venezia"),
        "filip stankovic": ("Stankovic F.", "Venezia"),
        "lorenzo montipo": ("Montipò", "Venezia"),
        "ridg pasture haps": ("Haps", "Venezia"),
        "ridgeciano haps": ("Haps", "Venezia"),
        "marin sverko": ("Sverko", "Venezia"),
        "alfred duncan": ("Duncan", "Venezia"),

        # Frosinone
        "ilario monterisi": ("Monterisi", "Frosinone"),
        "francesco gelli": ("Gelli F.", "Frosinone"),
        "ben lhassine kone": ("Kone B.", "Frosinone"),
        "alen sherri": ("Sherri", "Cagliari"),
        "luigi canotto": ("Canotto", "Frosinone"),
        "anthony oyono": ("Oyono A.", "Frosinone"),
        "giorgio cittadini": ("Cittadini", "Frosinone"),
        "alessio zerbin": ("Zerbin", "Frosinone"),
        "florian grillitsch": ("Grillitsch", "Frosinone"),
        "luis hasa": ("Hasa", "Frosinone"),
        "antonio raimondo": ("Raimondo", "Frosinone"),

        # Monza
        "valentin antov": ("Antov", "Monza"),
        "adam bakoune": ("Bakoune", "Monza"),
        "omari forson": ("Forson O.", "Monza"),
        "patrick cutrone": ("Cutrone", "Monza"),
        "michael folorunsho": ("Folorunsho", "Monza"),
        "cyril ngonge": ("Ngonge", "Monza"),
        "dany mota": ("Mota", "Monza"),
        "andrea colpani": ("Colpani", "Monza"),
        "matteo pessina": ("Pessina", "Monza"),
        "samuele birindelli": ("Birindelli", "Monza"),
        "patrick ciurria": ("Ciurria", "Monza"),
        "andrea carboni": ("Carboni A.", "Monza"),

        # Fiorentina
        "luca lezzerini": ("Lezzerini", "Fiorentina"),
        "fabiano parisi": ("Parisi", "Fiorentina"),
        "dodo": ("Dodò", "Fiorentina"),
        "rolando mandragora": ("Mandragora", "Fiorentina"),
        "marco brescianini": ("Brescianini", "Fiorentina"),
        "albert gudmundsson": ("Gudmundsson A.", "Fiorentina"),
        "moise kean": ("Kean", "Fiorentina"),
        "david de gea": ("De Gea", "Fiorentina"),
        "oliver christensen": ("Christensen O.", "Fiorentina"),
        "marin pongracic": ("Pongracic", "Fiorentina"),
        "luca ranieri": ("Ranieri L.", "Fiorentina"),
        "nicolò fagioli": ("Fagioli", "Fiorentina"),
        "nicolo fagioli": ("Fagioli", "Fiorentina"),
        "cher ndour": ("Ndour", "Fiorentina"),
        "niccolo fortini": ("Fortini", "Torino"),
        "roberto piccoli": ("Piccoli", "Bologna"),
        "arthur atta": ("Atta", "Fiorentina"),

        # Genoa
        "alessandro marcandalli": ("Marcandalli", "Genoa"),
        "leo ostigard": ("Ostigard", "Genoa"),
        "sebastian otoa": ("Otoa", "Genoa"),
        "brooke norton-cuffy": ("Norton-Cuffy", "Genoa"),
        "brooke nortoncuffy": ("Norton-Cuffy", "Genoa"),
        "morten frendrup": ("Frendrup", "Genoa"),
        "junior messias": ("Messias", "Genoa"),
        "tommaso baldanzi": ("Baldanzi", "Genoa"),
        "jeff ekhator": ("Ekhator", "Juventus"),
        "lorenzo venturino": ("Venturino", "Genoa"),
        "johan vasquez": ("Vasquez", "Genoa"),
        "aaron martin": ("Martin", "Genoa"),
        "stefano sabelli": ("Sabelli", "Genoa"),
        "lorenzo colombo": ("Colombo", "Genoa"),
        "vitinha": ("Vitinha O.", "Genoa"),

        # Lecce
        "gaspar": ("Gaspar K.", "Lecce"),
        "gaby jean": ("Jean", "Lecce"),
        "antonino gallo": ("Gallo", "Lecce"),
        "sadik fofana": ("Fofana Sa.", "Lecce"),
        "medon berisha": ("Berisha M.", "Lecce"),
        "mohamed kaba": ("Kaba", "Lecce"),
        "lassana coulibaly": ("Coulibaly L.", "Lecce"),
        "wladimiro falcone": ("Falcone", "Lecce"),
        "marco bleve": ("Bleve", "Lecce"),
        "santiago pierotti": ("Pierotti", "Lecce"),
        "youssef maleh": ("Maleh", "Lecce"),
        "francesco camarda": ("Camarda", "Milan"),

        # Torino
        "ardian ismajli": ("Ismajli", "Torino"),
        "cristiano biraghi": ("Biraghi", "Torino"),
        "gvidas gineitis": ("Gineitis", "Torino"),
        "tino anjorin": ("Anjorin", "Torino"),
        "alieu njie": ("Njie", "Torino"),
        "zakaria aboukhlal": ("Aboukhlal", "Torino"),
        "giovanni simeone": ("Simeone", "Torino"),
        "che adams": ("Adams C.", "Torino"),
        "duvan zapata": ("Zapata D.", "Torino"),
        "nikola vlasic": ("Vlasic", "Torino"),
        "saul coco": ("Coco", "Torino"),
        "cesare casadei": ("Casadei", "Torino"),
        "gaetano oristanio": ("Oristanio", "Torino"),
        "ivan ilic": ("Ilic", "Lecce"),
        "rafa obrador": ("Obrador", "Sassuolo"),

        # Parma
        "abdoulaye ndiaye": ("Ndiaye", "Parma"),
        "lautaro valenti": ("Valenti", "Parma"),
        "emanuele valeri": ("Valeri", "Parma"),
        "sascha britschgi": ("Britschgi", "Parma"),
        "mandela keita": ("Keita M.", "Parma"),
        "adrian bernabe": ("Bernabè", "Parma"),
        "benja cremaschi": ("Cremaschi", "Parma"),
        "pontus almqvist": ("Almqvist", "Parma"),
        "matija frigan": ("Frigan", "Parma"),
        "nesta elphege": ("Elphege", "Parma"),
        "enrico delprato": ("Delprato", "Parma"),

        # Cagliari
        "boris radunovic": ("Radunovic", "Cagliari"),
        "juan rodriguez": ("Rodriguez Ju.", "Cagliari"),
        "ze pedro": ("Zè Pedro", "Cagliari"),
        "yerry mina": ("Mina", "Cagliari"),
        "riyad idrissi": ("Idrissi R.", "Cagliari"),
        "joseph liteta": ("Liteta", "Cagliari"),
        "alessandro deiola": ("Deiola", "Cagliari"),
        "mattia felici": ("Felici", "Cagliari"),
        "gennaro borrelli": ("Borrelli", "Cagliari"),
        "daniel maldini": ("Maldini", "Cagliari"),
        "alieu fadera": ("Fadera", "Cagliari"),
        "gianluca gaetano": ("Gaetano", "Atalanta"),
        "elio caprile": ("Caprile", "Cagliari"),
        "alend sherri": ("Sherri", "Cagliari"),
        "adam obert": ("Obert", "Cagliari"),
        "antoine makoumbou": ("Makoumbou", "Cagliari"),
        "michel adopo": ("Adopo", "Cagliari"),
        "jacopo fazzini": ("Fazzini", "Cagliari"),
        "harry winks": ("Winks", "Cagliari"),
        "kingstone mutandwa": ("Mutandwa", "Cagliari"),

        # Sassuolo
        "arijanet muric": ("Muric", "Sassuolo"),
        "stefano turati": ("Turati", "Sassuolo"),
        "giacomo satalino": ("Satalino", "Sassuolo"),
        "alessandro russo": ("Russo A.", "Sassuolo"),
        "jay idzes": ("Idzes", "Sassuolo"),
        "fali cande": ("Candè", "Sassuolo"),
        "cas odenthal": ("Odenthal", "Sassuolo"),
        "tommaso macchioni": ("Macchioni", "Sassuolo"),
        "josh doig": ("Doig", "Sassuolo"),
        "edoardo pieragnolo": ("Pieragnolo", "Sassuolo"),
        "sebastian walukiewicz": ("Walukiewicz", "Sassuolo"),
        "filippo missori": ("Missori", "Sassuolo"),
        "luca lipani": ("Lipani", "Sassuolo"),
        "daniel boloca": ("Boloca", "Sassuolo"),
        "nemanja matic": ("Matic", "Sassuolo"),
        "ismael kone": ("Konè I.", "Sassuolo"),
        "kristian thorstvedt": ("Thorstvedt", "Sassuolo"),
        "darryl bakola": ("Bakola", "Sassuolo"),
        "edoardo iannoni": ("Iannoni", "Sassuolo"),
        "cristian volpato": ("Volpato", "Sassuolo"),
        "armand lauriente": ("Laurientè", "Sassuolo"),
        "domenico berardi": ("Berardi", "Sassuolo"),
        "andrea pinamonti": ("Pinamonti", "Lazio"),

        # Udinese
        "maduka okoye": ("Okoye", "Udinese"),
        "daniele padelli": ("Padelli", "Udinese"),
        "oumar solet": ("Solet", "Udinese"),
        "nicolo bertola": ("Bertola", "Udinese"),
        "matteo palma": ("Palma", "Udinese"),
        "branimir mlacic": ("Mlacic", "Udinese"),
        "christian kabasele": ("Kabasele", "Udinese"),
        "hassane kamara": ("Kamara H.", "Udinese"),
        "alessandro zanoli": ("Zanoli", "Udinese"),
        "jesper karlstrom": ("Karlstrom", "Udinese"),
        "jurgen ekkelenkamp": ("Ekkelenkamp", "Udinese"),
        "lennon miller": ("Miller L.", "Udinese"),
        "jakub piotrowski": ("Piotrowski", "Udinese"),
        "oier zarraga": ("Zarraga", "Udinese"),
        "juan arizala": ("Arizala", "Udinese"),
        "nicolo zaniolo": ("Zaniolo", "Udinese"),
        "keinan davis": ("Davis K.", "Udinese"),
        "idrissa gueye": ("Gueye", "Udinese"),
        "vakoun bayo": ("Bayo V.", "Udinese"),
        "thomas kristensen": ("Kristensen T.", "Atalanta"),
        "mergim vojvoda": ("Vojvoda", "Udinese"),

        # Lazio
        "christos mandas": ("Mandas", "Lazio"),
        "edoardo motta": ("Motta", "Lazio"),
        "ivan provedel": ("Provedel", "Inter"),
        "mario gila": ("Gila", "Milan"),
        "oliver provstgaard": ("Provstgaard", "Lazio"),
        "alessio romagnoli": ("Romagnoli", "Lazio"),
        "patric": ("Patric", "Lazio"),
        "nuno tavares": ("Tavares N.", "Lazio"),
        "luca pellegrini": ("Pellegrini Lu.", "Lazio"),
        "adam marusic": ("Marusic", "Lazio"),
        "manuel lazzari": ("Lazzari", "Lazio"),
        "nicolo rovella": ("Rovella", "Lazio"),
        "reda belahyane": ("Belahyane", "Lazio"),
        "danilo cataldi": ("Cataldi", "Lazio"),
        "kenneth taylor": ("Taylor K.", "Lazio"),
        "fisayo dele-bashiru": ("Dele-Bashiru", "Lazio"),
        "fisayo delebashiru": ("Dele-Bashiru", "Lazio"),
        "adrian przyborek": ("Przyborek", "Lazio"),
        "mattia zaccagni": ("Zaccagni", "Lazio"),
        "gustav isaksen": ("Isaksen", "Lazio"),
        "tijjani noslin": ("Noslin", "Lazio"),
        "matteo cancellieri": ("Cancellieri", "Lazio"),
        "petar ratkov": ("Ratkov", "Lazio"),
        "boulaye dia": ("Dia", "Lazio"),

        # Bologna
        "lukasz skorupski": ("Skorupski", "Bologna"),
        "federico ravaglia": ("Ravaglia F.", "Bologna"),
        "torbjorn heggem": ("Heggem", "Bologna"),
        "martin vitik": ("Vitik", "Bologna"),
        "eivind helland": ("Helland", "Bologna"),
        "nicolo casale": ("Casale", "Bologna"),
        "juan miranda": ("Miranda J.", "Bologna"),
        "charalabos lykogiannis": ("Lykogiannis", "Bologna"),
        "emil holm": ("Holm", "Bologna"),
        "joao mario": ("Joao Mario", "Fiorentina"),
        "nadir zortea": ("Zortea", "Bologna"),
        "lorenzo de silvestri": ("De Silvestri", "Bologna"),
        "nikola moro": ("Moro N.", "Bologna"),
        "ibrahim sulemana": ("Sulemana I.", "Atalanta"),
        "lewis ferguson": ("Ferguson", "Bologna"),
        "tommaso pobega": ("Pobega", "Bologna"),
        "simon sohm": ("Sohm", "Venezia"),
        "remo freuler": ("Freuler", "Bologna"),
        "jens odgaard": ("Odgaard", "Bologna"),
        "giovanni fabbian": ("Fabbian", "Parma"),
        "kacper urbanski": ("Urbanski", "Bologna"),
        "jonathan rowe": ("Rowe", "Bologna"),
        "nicolo cambiaghi": ("Cambiaghi", "Bologna"),
        "benja dominguez": ("Dominguez B.", "Bologna"),
        "jesper karlsson": ("Karlsson", "Bologna"),
        "riccardo orsolini": ("Orsolini", "Bologna"),
        "federico bernardeschi": ("Bernardeschi", "Bologna"),
        "thijs dallinga": ("Dallinga", "Bologna"),
        "ciro immobile": ("Immobile", "Bologna"),
        "massimo pessina": ("Pessina Mas.", "Bologna"),
        "jhon lucumi": ("Lucumì", "Juventus"),
        "jonathan david": ("David", "Juventus"),

        # Atalanta
        "sead kolasinac": ("Kolasinac", "Atalanta"),
        "raoul bellanova": ("Bellanova", "Atalanta"),
        "giorgio scalvini": ("Scalvini", "Atalanta"),
        "gianluca scamacca": ("Scamacca", "Atalanta"),
        "charles de ketelaere": ("De Ketelaere", "Atalanta"),
        "ederson": ("Ederson D.S.", "Atalanta"),
        "lorenzo bernasconi": ("Bernasconi", "Atalanta"),
        "isak hien": ("Hien", "Atalanta"),
        "giacomo raspadori": ("Raspadori", "Atalanta"),
        "kamaldeen sulemana": ("Sulemana K.", "Atalanta"),
        "odilon kossounou": ("Kossounou", "Atalanta"),
        "nicola zalewski": ("Zalewski", "Atalanta"),
        "marten de roon": ("De Roon", "Atalanta"),
        "honest ahanor": ("Ahanor", "Atalanta"),
        "marco carnesecchi": ("Carnesecchi", "Atalanta"),
        "marco sportiello": ("Sportiello", "Atalanta"),
        "davide zappacosta": ("Zappacosta", "Atalanta"),
        "lazar samardzic": ("Samardzic", "Atalanta"),
        "mario pasalic": ("Pasalic", "Atalanta"),
        "nikola krstovic": ("Krstovic", "Atalanta")
    }

    explicit_map = {norm(k): v for k, v in raw_explicit_map.items()}

    if norm_tm in explicit_map:
        res = explicit_map[norm_tm]
        if res is None or res[0] == "IGNORE":
            return None
        target_name, target_team = res
        for p in listone_players:
            if p['name'].lower() == target_name.lower() and p['team'].lower() == target_team.lower():
                return p

    # Mappa ruoli compatibili
    role_map = {
        'POR': {'P'},
        'DC': {'D'}, 'TS': {'D'}, 'TD': {'D'},
        'M': {'C'}, 'CC': {'C'}, 'CD': {'C', 'D'}, 'CS': {'C', 'D'}, 'TQ': {'C', 'A'},
        'AS': {'C', 'A'}, 'AD': {'C', 'A'}, 'SP': {'A', 'C'}, 'P': {'A'}
    }
    allowed_roles = role_map.get(pos_tm, {'P', 'D', 'C', 'A'})

    # Fallback ricerca automatica
    for p in listone_players:
        if p['role'] not in allowed_roles:
            continue
        norm_p = norm(p['name'])
        if norm_p == norm_tm:
            return p
        if len(norm_p) >= 4 and (norm_p in norm_tm or norm_tm in norm_p):
            return p

    return None

def process_scraped_team(team_scraped_name, html_content):
    db = load_or_init_db()
    df_quot = load_quotazioni()
    
    listone_players = []
    for _, row in df_quot.iterrows():
        listone_players.append({
            'id': int(row.get('Id', 0)),
            'name': str(row.get('Nome', '')).strip(),
            'role': str(row.get('R', '')).strip().upper(),
            'team': str(row.get('Squadra', '')).strip(),
            'fvm': float(row.get('FVM', 1.0))
        })

    tm_players = parse_transfermarkt_html(html_content)
    updated_count = 0
    matched_log = []

    for tm_name, tm_data in tm_players.items():
        matched_p = match_tm_player_to_listone(tm_name, tm_data, listone_players)
        if matched_p:
            pname = matched_p['name']
            pteam = matched_p['team']
            
            missed = tm_data['injuries_count']
            inj_list = tm_data['injuries']
            giornate_all = [g for g, _ in inj_list]
            
            diag_dict = {}
            for g, diag in inj_list:
                diag_dict.setdefault(diag, []).append(g)
            
            diagnosi_formatted = []
            for diag_name, g_list in diag_dict.items():
                diagnosi_formatted.append({
                    "motivo": diag_name,
                    "partite": len(g_list),
                    "giornate": g_list
                })

            if missed >= 10: frag_level = "🔴 Alta"
            elif missed >= 4: frag_level = "🟡 Media"
            else: frag_level = "🟢 Bassa"

            if pteam not in db:
                db[pteam] = {}

            db[pteam][pname] = {
                "id": matched_p['id'],
                "ruolo": matched_p['role'],
                "fvm": matched_p['fvm'],
                "in_rosa_2627": True,
                "squadra_2627": pteam,
                "squadra_tm_2526": team_scraped_name,
                "tm_matched_name": tm_name,
                "partite_saltate": missed,
                "giornate_saltate": giornate_all,
                "diagnosi": diagnosi_formatted,
                "livello_fragilita": frag_level
            }
            updated_count += 1
            matched_log.append((matched_p, tm_name, missed, diag_dict))

    # Salva database
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

    print(f"✓ Elaborato {team_scraped_name}: {updated_count} calciatori matchati con successo nel listone 26/27!")
    return matched_log

if __name__ == "__main__":
    # Inizializza o aggiorna tutto
    pass
