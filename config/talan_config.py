"""
Configuration spécifique pour Talan Tunisie
Informations entreprise, services, positionnement, formats de messages
"""

TALAN_COMPANY_INFO = {
    "name": "Talan Tunisie",
    "industry": "Conseil en transformation digitale",
    "location": "Tunis, Tunisie",
    "founded": "Filiale du groupe Talan international",
    "employees": "200+ consultants certifiés",
    "languages": ["Français", "Arabe", "Anglais"],
    
    "services": {
        "transformation_digitale": {
            "title": "Transformation Digitale",
            "description": "Accompagnement stratégique et opérationnel dans la digitalisation",
            "value_props": ["Méthodologie éprouvée", "Expertise locale", "ROI mesurable"]
        },
        "cloud": {
            "title": "Solutions Cloud",
            "description": "Migration et optimisation cloud (AWS, Azure, Google Cloud)",
            "value_props": ["Sécurité renforcée", "Scalabilité", "Réduction des coûts"]
        },
        "data_ai": {
            "title": "Data & Intelligence Artificielle",
            "description": "Analytics, BI, Machine Learning et IA générative",
            "value_props": ["Insights actionnables", "Automatisation", "Aide à la décision"]
        },
        "erp": {
            "title": "Solutions ERP",
            "description": "Implémentation SAP, Oracle, Microsoft Dynamics",
            "value_props": ["Intégration complète", "Processus optimisés", "Formation incluse"]
        },
        "cybersecurity": {
            "title": "Cybersécurité",
            "description": "Audit, protection, conformité et gouvernance",
            "value_props": ["Protection 24/7", "Conformité réglementaire", "Risk management"]
        }
    },
    
    "competitive_advantages": [
        "Expertise locale avec standards internationaux",
        "Équipe multilingue (FR/AR/EN)",
        "Présence physique en Tunisie",
        "Track record de 150+ projets réussis",
        "Partenaire officiel des leaders technologiques",
        "Méthodologies agiles et DevOps"
    ],
    
    "target_industries": [
        "Banques et Services Financiers",
        "Télécommunications",
        "Industrie et Manufacturing", 
        "Services Publics",
        "Santé",
        "Retail et Distribution"
    ]
}

# Formats de messages selon le channel
MESSAGE_FORMATS = {
    "email": {
        "structure": ["greeting", "introduction", "value_proposition", "call_to_action", "signature"],
        "tone": "Formel et professionnel",
        "length": "Détaillé (300-500 mots)",
        "elements": ["Objet accrocheur", "Formule de politesse", "Signature complète"]
    },
    "linkedin": {
        "structure": ["hook", "brief_intro", "value", "cta"],
        "tone": "Professionnel mais direct",
        "length": "Concis (150-250 mots)",
        "elements": ["Message personnalisé", "Mention du profil", "CTA clair"]
    },
    "phone": {
        "structure": ["introduction", "discovery", "presentation", "objection_handling", "closing"],
        "tone": "Conversationnel et chaleureux",
        "length": "Script structuré",
        "elements": ["Questions ouvertes", "Écoute active", "Rebond sur objections"]
    },
    "meeting": {
        "structure": ["welcome", "agenda", "presentation", "demo", "next_steps"],
        "tone": "Consultative et experte",
        "length": "Présentation complète",
        "elements": ["Support visuel", "Démonstration", "Q&A"]
    }
}

# Types de messages et leurs objectifs
MESSAGE_TYPES = {
    "opening": {
        "objective": "Capter l'attention et créer l'intérêt",
        "key_elements": ["Accroche personnalisée", "Compréhension des enjeux", "Teaser de valeur"]
    },
    "follow_up": {
        "objective": "Maintenir l'engagement et approfondir",
        "key_elements": ["Référence à l'échange précédent", "Nouvelle information", "Progression"]
    },
    "qualification": {
        "objective": "Comprendre les besoins et la situation",
        "key_elements": ["Questions ciblées", "Découverte des enjeux", "Mapping des décideurs"]
    },
    "presentation": {
        "objective": "Présenter la solution adaptée",
        "key_elements": ["Solution sur-mesure", "Bénéfices métier", "Preuves de concept"]
    },
    "objection_handling": {
        "objective": "Traiter les objections et rassurer",
        "key_elements": ["Écoute empathique", "Réponse argumentée", "Preuves sociales"]
    },
    "closing": {
        "objective": "Obtenir l'engagement et les prochaines étapes",
        "key_elements": ["Récapitulatif des bénéfices", "Urgence", "Action concrète"]
    }
}
