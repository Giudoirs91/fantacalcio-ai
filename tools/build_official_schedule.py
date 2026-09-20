import json
import os

CALENDARIO_DATA = [
    {
        "giornata": 1,
        "date": "23/08/2026",
        "matches": [
            {"home": "Atalanta", "away": "Sassuolo"},
            {"home": "Bologna", "away": "Lazio"},
            {"home": "Frosinone", "away": "Juventus"},
            {"home": "Genoa", "away": "Napoli"},
            {"home": "Inter", "away": "Monza"},
            {"home": "Parma", "away": "Cagliari"},
            {"home": "Roma", "away": "Fiorentina"},
            {"home": "Torino", "away": "Milan"},
            {"home": "Udinese", "away": "Como"},
            {"home": "Venezia", "away": "Lecce"}
        ]
    },
    {
        "giornata": 2,
        "date": "30/08/2026",
        "matches": [
            {"home": "Atalanta", "away": "Bologna"},
            {"home": "Cagliari", "away": "Inter"},
            {"home": "Fiorentina", "away": "Frosinone"},
            {"home": "Juventus", "away": "Parma"},
            {"home": "Lazio", "away": "Genoa"},
            {"home": "Lecce", "away": "Roma"},
            {"home": "Milan", "away": "Venezia"},
            {"home": "Monza", "away": "Udinese"},
            {"home": "Napoli", "away": "Como"},
            {"home": "Sassuolo", "away": "Torino"}
        ]
    },
    {
        "giornata": 3,
        "date": "06/09/2026",
        "matches": [
            {"home": "Bologna", "away": "Sassuolo"},
            {"home": "Cagliari", "away": "Lecce"},
            {"home": "Fiorentina", "away": "Torino"},
            {"home": "Frosinone", "away": "Venezia"},
            {"home": "Genoa", "away": "Como"},
            {"home": "Inter", "away": "Napoli"},
            {"home": "Juventus", "away": "Milan"},
            {"home": "Parma", "away": "Monza"},
            {"home": "Roma", "away": "Atalanta"},
            {"home": "Udinese", "away": "Lazio"}
        ]
    },
    {
        "giornata": 4,
        "date": "13/09/2026",
        "matches": [
            {"home": "Atalanta", "away": "Cagliari"},
            {"home": "Como", "away": "Parma"},
            {"home": "Genoa", "away": "Frosinone"},
            {"home": "Inter", "away": "Udinese"},
            {"home": "Lazio", "away": "Milan"},
            {"home": "Lecce", "away": "Monza"},
            {"home": "Napoli", "away": "Bologna"},
            {"home": "Sassuolo", "away": "Juventus"},
            {"home": "Torino", "away": "Roma"},
            {"home": "Venezia", "away": "Fiorentina"}
        ]
    },
    {
        "giornata": 5,
        "date": "20/09/2026",
        "matches": [
            {"home": "Bologna", "away": "Torino"},
            {"home": "Fiorentina", "away": "Napoli"},
            {"home": "Frosinone", "away": "Como"},
            {"home": "Juventus", "away": "Atalanta"},
            {"home": "Milan", "away": "Lecce"},
            {"home": "Monza", "away": "Sassuolo"},
            {"home": "Parma", "away": "Genoa"},
            {"home": "Roma", "away": "Inter"},
            {"home": "Udinese", "away": "Cagliari"},
            {"home": "Venezia", "away": "Lazio"}
        ]
    },
    {
        "giornata": 6,
        "date": "11/10/2026",
        "matches": [
            {"home": "Atalanta", "away": "Venezia"},
            {"home": "Cagliari", "away": "Juventus"},
            {"home": "Como", "away": "Roma"},
            {"home": "Genoa", "away": "Fiorentina"},
            {"home": "Inter", "away": "Parma"},
            {"home": "Lazio", "away": "Monza"},
            {"home": "Lecce", "away": "Bologna"},
            {"home": "Napoli", "away": "Frosinone"},
            {"home": "Sassuolo", "away": "Milan"},
            {"home": "Torino", "away": "Udinese"}
        ]
    },
    {
        "giornata": 7,
        "date": "18/10/2026",
        "matches": [
            {"home": "Bologna", "away": "Inter"},
            {"home": "Fiorentina", "away": "Como"},
            {"home": "Frosinone", "away": "Sassuolo"},
            {"home": "Juventus", "away": "Lazio"},
            {"home": "Milan", "away": "Atalanta"},
            {"home": "Monza", "away": "Cagliari"},
            {"home": "Parma", "away": "Torino"},
            {"home": "Roma", "away": "Genoa"},
            {"home": "Udinese", "away": "Lecce"},
            {"home": "Venezia", "away": "Napoli"}
        ]
    },
    {
        "giornata": 8,
        "date": "25/10/2026",
        "matches": [
            {"home": "Atalanta", "away": "Frosinone"},
            {"home": "Cagliari", "away": "Bologna"},
            {"home": "Como", "away": "Sassuolo"},
            {"home": "Genoa", "away": "Venezia"},
            {"home": "Inter", "away": "Fiorentina"},
            {"home": "Lazio", "away": "Parma"},
            {"home": "Lecce", "away": "Juventus"},
            {"home": "Napoli", "away": "Roma"},
            {"home": "Torino", "away": "Monza"},
            {"home": "Udinese", "away": "Milan"}
        ]
    },
    {
        "giornata": 9,
        "date": "28/10/2026",
        "matches": [
            {"home": "Fiorentina", "away": "Atalanta"},
            {"home": "Frosinone", "away": "Lecce"},
            {"home": "Genoa", "away": "Juventus"},
            {"home": "Milan", "away": "Bologna"},
            {"home": "Monza", "away": "Napoli"},
            {"home": "Parma", "away": "Udinese"},
            {"home": "Roma", "away": "Cagliari"},
            {"home": "Sassuolo", "away": "Lazio"},
            {"home": "Torino", "away": "Como"},
            {"home": "Venezia", "away": "Inter"}
        ]
    },
    {
        "giornata": 10,
        "date": "01/11/2026",
        "matches": [
            {"home": "Atalanta", "away": "Parma"},
            {"home": "Bologna", "away": "Monza"},
            {"home": "Como", "away": "Venezia"},
            {"home": "Frosinone", "away": "Torino"},
            {"home": "Juventus", "away": "Napoli"},
            {"home": "Lazio", "away": "Cagliari"},
            {"home": "Lecce", "away": "Genoa"},
            {"home": "Milan", "away": "Inter"},
            {"home": "Sassuolo", "away": "Fiorentina"},
            {"home": "Udinese", "away": "Roma"}
        ]
    },
    {
        "giornata": 11,
        "date": "08/11/2026",
        "matches": [
            {"home": "Cagliari", "away": "Frosinone"},
            {"home": "Fiorentina", "away": "Juventus"},
            {"home": "Genoa", "away": "Milan"},
            {"home": "Inter", "away": "Como"},
            {"home": "Monza", "away": "Atalanta"},
            {"home": "Napoli", "away": "Lazio"},
            {"home": "Parma", "away": "Bologna"},
            {"home": "Roma", "away": "Sassuolo"},
            {"home": "Torino", "away": "Lecce"},
            {"home": "Venezia", "away": "Udinese"}
        ]
    },
    {
        "giornata": 12,
        "date": "22/11/2026",
        "matches": [
            {"home": "Atalanta", "away": "Inter"},
            {"home": "Bologna", "away": "Udinese"},
            {"home": "Como", "away": "Cagliari"},
            {"home": "Juventus", "away": "Venezia"},
            {"home": "Lazio", "away": "Lecce"},
            {"home": "Milan", "away": "Frosinone"},
            {"home": "Monza", "away": "Fiorentina"},
            {"home": "Napoli", "away": "Torino"},
            {"home": "Parma", "away": "Roma"},
            {"home": "Sassuolo", "away": "Genoa"}
        ]
    },
    {
        "giornata": 13,
        "date": "29/11/2026",
        "matches": [
            {"home": "Cagliari", "away": "Milan"},
            {"home": "Como", "away": "Juventus"},
            {"home": "Frosinone", "away": "Parma"},
            {"home": "Inter", "away": "Genoa"},
            {"home": "Lecce", "away": "Atalanta"},
            {"home": "Roma", "away": "Monza"},
            {"home": "Sassuolo", "away": "Napoli"},
            {"home": "Torino", "away": "Lazio"},
            {"home": "Udinese", "away": "Fiorentina"},
            {"home": "Venezia", "away": "Bologna"}
        ]
    },
    {
        "giornata": 14,
        "date": "06/12/2026",
        "matches": [
            {"home": "Bologna", "away": "Roma"},
            {"home": "Fiorentina", "away": "Cagliari"},
            {"home": "Frosinone", "away": "Inter"},
            {"home": "Genoa", "away": "Torino"},
            {"home": "Juventus", "away": "Udinese"},
            {"home": "Lazio", "away": "Atalanta"},
            {"home": "Milan", "away": "Parma"},
            {"home": "Monza", "away": "Como"},
            {"home": "Napoli", "away": "Lecce"},
            {"home": "Venezia", "away": "Sassuolo"}
        ]
    },
    {
        "giornata": 15,
        "date": "13/12/2026",
        "matches": [
            {"home": "Atalanta", "away": "Genoa"},
            {"home": "Cagliari", "away": "Venezia"},
            {"home": "Como", "away": "Bologna"},
            {"home": "Inter", "away": "Torino"},
            {"home": "Juventus", "away": "Monza"},
            {"home": "Lazio", "away": "Roma"},
            {"home": "Lecce", "away": "Sassuolo"},
            {"home": "Napoli", "away": "Milan"},
            {"home": "Parma", "away": "Fiorentina"},
            {"home": "Udinese", "away": "Frosinone"}
        ]
    },
    {
        "giornata": 16,
        "date": "20/12/2026",
        "matches": [
            {"home": "Atalanta", "away": "Napoli"},
            {"home": "Fiorentina", "away": "Bologna"},
            {"home": "Frosinone", "away": "Lazio"},
            {"home": "Genoa", "away": "Udinese"},
            {"home": "Lecce", "away": "Inter"},
            {"home": "Milan", "away": "Como"},
            {"home": "Roma", "away": "Juventus"},
            {"home": "Sassuolo", "away": "Parma"},
            {"home": "Torino", "away": "Cagliari"},
            {"home": "Venezia", "away": "Monza"}
        ]
    },
    {
        "giornata": 17,
        "date": "03/01/2027",
        "matches": [
            {"home": "Bologna", "away": "Juventus"},
            {"home": "Cagliari", "away": "Genoa"},
            {"home": "Como", "away": "Lecce"},
            {"home": "Fiorentina", "away": "Lazio"},
            {"home": "Inter", "away": "Sassuolo"},
            {"home": "Monza", "away": "Milan"},
            {"home": "Parma", "away": "Napoli"},
            {"home": "Roma", "away": "Frosinone"},
            {"home": "Torino", "away": "Venezia"},
            {"home": "Udinese", "away": "Atalanta"}
        ]
    },
    {
        "giornata": 18,
        "date": "06/01/2027",
        "matches": [
            {"home": "Atalanta", "away": "Como"},
            {"home": "Frosinone", "away": "Bologna"},
            {"home": "Genoa", "away": "Monza"},
            {"home": "Juventus", "away": "Torino"},
            {"home": "Lazio", "away": "Inter"},
            {"home": "Lecce", "away": "Parma"},
            {"home": "Milan", "away": "Fiorentina"},
            {"home": "Napoli", "away": "Cagliari"},
            {"home": "Sassuolo", "away": "Udinese"},
            {"home": "Venezia", "away": "Roma"}
        ]
    },
    {
        "giornata": 19,
        "date": "10/01/2027",
        "matches": [
            {"home": "Bologna", "away": "Genoa"},
            {"home": "Cagliari", "away": "Sassuolo"},
            {"home": "Como", "away": "Lazio"},
            {"home": "Fiorentina", "away": "Lecce"},
            {"home": "Inter", "away": "Juventus"},
            {"home": "Monza", "away": "Frosinone"},
            {"home": "Parma", "away": "Venezia"},
            {"home": "Roma", "away": "Milan"},
            {"home": "Torino", "away": "Atalanta"},
            {"home": "Udinese", "away": "Napoli"}
        ]
    },
    {
        "giornata": 20,
        "date": "17/01/2027",
        "matches": [
            {"home": "Atalanta", "away": "Roma"},
            {"home": "Cagliari", "away": "Como"},
            {"home": "Juventus", "away": "Genoa"},
            {"home": "Lazio", "away": "Bologna"},
            {"home": "Lecce", "away": "Udinese"},
            {"home": "Milan", "away": "Torino"},
            {"home": "Napoli", "away": "Fiorentina"},
            {"home": "Parma", "away": "Inter"},
            {"home": "Sassuolo", "away": "Monza"},
            {"home": "Venezia", "away": "Frosinone"}
        ]
    },
    {
        "giornata": 21,
        "date": "24/01/2027",
        "matches": [
            {"home": "Bologna", "away": "Atalanta"},
            {"home": "Como", "away": "Napoli"},
            {"home": "Fiorentina", "away": "Sassuolo"},
            {"home": "Frosinone", "away": "Milan"},
            {"home": "Genoa", "away": "Parma"},
            {"home": "Inter", "away": "Venezia"},
            {"home": "Juventus", "away": "Cagliari"},
            {"home": "Lecce", "away": "Torino"},
            {"home": "Monza", "away": "Lazio"},
            {"home": "Roma", "away": "Udinese"}
        ]
    },
    {
        "giornata": 22,
        "date": "31/01/2027",
        "matches": [
            {"home": "Atalanta", "away": "Fiorentina"},
            {"home": "Cagliari", "away": "Parma"},
            {"home": "Genoa", "away": "Lecce"},
            {"home": "Lazio", "away": "Venezia"},
            {"home": "Milan", "away": "Juventus"},
            {"home": "Monza", "away": "Roma"},
            {"home": "Napoli", "away": "Inter"},
            {"home": "Sassuolo", "away": "Como"},
            {"home": "Torino", "away": "Frosinone"},
            {"home": "Udinese", "away": "Bologna"}
        ]
    },
    {
        "giornata": 23,
        "date": "07/02/2027",
        "matches": [
            {"home": "Atalanta", "away": "Lazio"},
            {"home": "Bologna", "away": "Milan"},
            {"home": "Como", "away": "Monza"},
            {"home": "Fiorentina", "away": "Udinese"},
            {"home": "Inter", "away": "Cagliari"},
            {"home": "Juventus", "away": "Sassuolo"},
            {"home": "Lecce", "away": "Napoli"},
            {"home": "Parma", "away": "Frosinone"},
            {"home": "Roma", "away": "Torino"},
            {"home": "Venezia", "away": "Genoa"}
        ]
    },
    {
        "giornata": 24,
        "date": "14/02/2027",
        "matches": [
            {"home": "Bologna", "away": "Como"},
            {"home": "Cagliari", "away": "Lazio"},
            {"home": "Frosinone", "away": "Fiorentina"},
            {"home": "Genoa", "away": "Atalanta"},
            {"home": "Inter", "away": "Milan"},
            {"home": "Monza", "away": "Lecce"},
            {"home": "Napoli", "away": "Juventus"},
            {"home": "Roma", "away": "Parma"},
            {"home": "Torino", "away": "Sassuolo"},
            {"home": "Udinese", "away": "Venezia"}
        ]
    },
    {
        "giornata": 25,
        "date": "21/02/2027",
        "matches": [
            {"home": "Atalanta", "away": "Monza"},
            {"home": "Como", "away": "Torino"},
            {"home": "Fiorentina", "away": "Inter"},
            {"home": "Juventus", "away": "Bologna"},
            {"home": "Lazio", "away": "Napoli"},
            {"home": "Lecce", "away": "Frosinone"},
            {"home": "Milan", "away": "Genoa"},
            {"home": "Sassuolo", "away": "Roma"},
            {"home": "Udinese", "away": "Parma"},
            {"home": "Venezia", "away": "Cagliari"}
        ]
    },
    {
        "giornata": 26,
        "date": "28/02/2027",
        "matches": [
            {"home": "Bologna", "away": "Lecce"},
            {"home": "Cagliari", "away": "Udinese"},
            {"home": "Como", "away": "Milan"},
            {"home": "Frosinone", "away": "Napoli"},
            {"home": "Genoa", "away": "Lazio"},
            {"home": "Inter", "away": "Atalanta"},
            {"home": "Monza", "away": "Juventus"},
            {"home": "Parma", "away": "Sassuolo"},
            {"home": "Roma", "away": "Venezia"},
            {"home": "Torino", "away": "Fiorentina"}
        ]
    },
    {
        "giornata": 27,
        "date": "07/03/2027",
        "matches": [
            {"home": "Atalanta", "away": "Torino"},
            {"home": "Fiorentina", "away": "Venezia"},
            {"home": "Juventus", "away": "Roma"},
            {"home": "Lazio", "away": "Frosinone"},
            {"home": "Lecce", "away": "Como"},
            {"home": "Milan", "away": "Cagliari"},
            {"home": "Monza", "away": "Genoa"},
            {"home": "Napoli", "away": "Parma"},
            {"home": "Sassuolo", "away": "Bologna"},
            {"home": "Udinese", "away": "Inter"}
        ]
    },
    {
        "giornata": 28,
        "date": "14/03/2027",
        "matches": [
            {"home": "Bologna", "away": "Napoli"},
            {"home": "Cagliari", "away": "Fiorentina"},
            {"home": "Como", "away": "Udinese"},
            {"home": "Frosinone", "away": "Monza"},
            {"home": "Genoa", "away": "Roma"},
            {"home": "Lazio", "away": "Juventus"},
            {"home": "Milan", "away": "Sassuolo"},
            {"home": "Parma", "away": "Lecce"},
            {"home": "Torino", "away": "Inter"},
            {"home": "Venezia", "away": "Atalanta"}
        ]
    },
    {
        "giornata": 29,
        "date": "21/03/2027",
        "matches": [
            {"home": "Atalanta", "away": "Milan"},
            {"home": "Fiorentina", "away": "Genoa"},
            {"home": "Inter", "away": "Frosinone"},
            {"home": "Juventus", "away": "Como"},
            {"home": "Monza", "away": "Bologna"},
            {"home": "Napoli", "away": "Venezia"},
            {"home": "Parma", "away": "Lazio"},
            {"home": "Roma", "away": "Lecce"},
            {"home": "Sassuolo", "away": "Cagliari"},
            {"home": "Udinese", "away": "Torino"}
        ]
    },
    {
        "giornata": 30,
        "date": "04/04/2027",
        "matches": [
            {"home": "Cagliari", "away": "Napoli"},
            {"home": "Como", "away": "Fiorentina"},
            {"home": "Frosinone", "away": "Udinese"},
            {"home": "Genoa", "away": "Inter"},
            {"home": "Lecce", "away": "Lazio"},
            {"home": "Milan", "away": "Monza"},
            {"home": "Roma", "away": "Bologna"},
            {"home": "Sassuolo", "away": "Atalanta"},
            {"home": "Torino", "away": "Juventus"},
            {"home": "Venezia", "away": "Parma"}
        ]
    },
    {
        "giornata": 31,
        "date": "11/04/2027",
        "matches": [
            {"home": "Bologna", "away": "Venezia"},
            {"home": "Cagliari", "away": "Atalanta"},
            {"home": "Fiorentina", "away": "Milan"},
            {"home": "Frosinone", "away": "Genoa"},
            {"home": "Inter", "away": "Roma"},
            {"home": "Juventus", "away": "Lecce"},
            {"home": "Lazio", "away": "Torino"},
            {"home": "Napoli", "away": "Sassuolo"},
            {"home": "Parma", "away": "Como"},
            {"home": "Udinese", "away": "Monza"}
        ]
    },
    {
        "giornata": 32,
        "date": "18/04/2027",
        "matches": [
            {"home": "Atalanta", "away": "Udinese"},
            {"home": "Bologna", "away": "Cagliari"},
            {"home": "Como", "away": "Frosinone"},
            {"home": "Fiorentina", "away": "Parma"},
            {"home": "Milan", "away": "Napoli"},
            {"home": "Monza", "away": "Inter"},
            {"home": "Roma", "away": "Lazio"},
            {"home": "Sassuolo", "away": "Lecce"},
            {"home": "Torino", "away": "Genoa"},
            {"home": "Venezia", "away": "Juventus"}
        ]
    },
    {
        "giornata": 33,
        "date": "25/04/2027",
        "matches": [
            {"home": "Cagliari", "away": "Monza"},
            {"home": "Frosinone", "away": "Roma"},
            {"home": "Genoa", "away": "Sassuolo"},
            {"home": "Inter", "away": "Bologna"},
            {"home": "Juventus", "away": "Fiorentina"},
            {"home": "Lazio", "away": "Como"},
            {"home": "Lecce", "away": "Milan"},
            {"home": "Napoli", "away": "Udinese"},
            {"home": "Parma", "away": "Atalanta"},
            {"home": "Venezia", "away": "Torino"}
        ]
    },
    {
        "giornata": 34,
        "date": "02/05/2027",
        "matches": [
            {"home": "Atalanta", "away": "Juventus"},
            {"home": "Bologna", "away": "Fiorentina"},
            {"home": "Como", "away": "Inter"},
            {"home": "Lecce", "away": "Cagliari"},
            {"home": "Milan", "away": "Lazio"},
            {"home": "Monza", "away": "Venezia"},
            {"home": "Roma", "away": "Napoli"},
            {"home": "Sassuolo", "away": "Frosinone"},
            {"home": "Torino", "away": "Parma"},
            {"home": "Udinese", "away": "Genoa"}
        ]
    },
    {
        "giornata": 35,
        "date": "09/05/2027",
        "matches": [
            {"home": "Fiorentina", "away": "Roma"},
            {"home": "Frosinone", "away": "Atalanta"},
            {"home": "Genoa", "away": "Cagliari"},
            {"home": "Inter", "away": "Lecce"},
            {"home": "Lazio", "away": "Sassuolo"},
            {"home": "Napoli", "away": "Monza"},
            {"home": "Parma", "away": "Milan"},
            {"home": "Torino", "away": "Bologna"},
            {"home": "Udinese", "away": "Juventus"},
            {"home": "Venezia", "away": "Como"}
        ]
    },
    {
        "giornata": 36,
        "date": "16/05/2027",
        "matches": [
            {"home": "Bologna", "away": "Frosinone"},
            {"home": "Cagliari", "away": "Torino"},
            {"home": "Como", "away": "Atalanta"},
            {"home": "Juventus", "away": "Inter"},
            {"home": "Lazio", "away": "Udinese"},
            {"home": "Lecce", "away": "Fiorentina"},
            {"home": "Milan", "away": "Roma"},
            {"home": "Monza", "away": "Parma"},
            {"home": "Napoli", "away": "Genoa"},
            {"home": "Sassuolo", "away": "Venezia"}
        ]
    },
    {
        "giornata": 37,
        "date": "23/05/2027",
        "matches": [
            {"home": "Atalanta", "away": "Lecce"},
            {"home": "Fiorentina", "away": "Monza"},
            {"home": "Frosinone", "away": "Cagliari"},
            {"home": "Genoa", "away": "Bologna"},
            {"home": "Inter", "away": "Lazio"},
            {"home": "Parma", "away": "Juventus"},
            {"home": "Roma", "away": "Como"},
            {"home": "Torino", "away": "Napoli"},
            {"home": "Udinese", "away": "Sassuolo"},
            {"home": "Venezia", "away": "Milan"}
        ]
    },
    {
        "giornata": 38,
        "date": "30/05/2027",
        "matches": [
            {"home": "Bologna", "away": "Parma"},
            {"home": "Cagliari", "away": "Roma"},
            {"home": "Como", "away": "Genoa"},
            {"home": "Juventus", "away": "Frosinone"},
            {"home": "Lazio", "away": "Fiorentina"},
            {"home": "Lecce", "away": "Venezia"},
            {"home": "Milan", "away": "Udinese"},
            {"home": "Monza", "away": "Torino"},
            {"home": "Napoli", "away": "Atalanta"},
            {"home": "Sassuolo", "away": "Inter"}
        ]
    }
]

def save_calendario():
    paths = [
        "data/processed/calendario_serie_a_2026_27.json",
        "config/calendario_serie_a_2026_27.json"
    ]
    for p in paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(CALENDARIO_DATA, f, ensure_ascii=False, indent=2)
        print(f"Salvato calendario in: {p} ({len(CALENDARIO_DATA)} giornate, {sum(len(g['matches']) for g in CALENDARIO_DATA)} partite totali)")

if __name__ == "__main__":
    save_calendario()
