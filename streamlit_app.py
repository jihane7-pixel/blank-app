import streamlit as st
from PIL import Image
import base64
import os
import sys
import math
import subprocess
import tempfile
import io
import datetime


try:
    from fpdf import FPDF
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf2"])
    from fpdf import FPDF



# Initialiser la session state pour garder les résultats
if "resultats_machines" not in st.session_state:
    st.session_state["resultats_machines"] = {}

st.set_page_config(layout="wide")

st.markdown("""
    <style>
        /* Tout le texte standard (paragraphes, infos, inputs, etc.) */
        html, body, [class*="css"]  {
            font-size: 16px !important;
        }

        /* Agrandir les titres */
        h1, h2, h3, h4, h5, h6 {
            font-size: 22px !important;
        }

        /* Agrandir aussi les boîtes d’info/succès/erreur si souhaité */
        .stAlert {
            font-size: 16px !important;
        }
    </style>
""", unsafe_allow_html=True)



logo1_path = "logo.jpg"
logo2_path = "logo cosumar.png"

col1, col2, col3 = st.columns([2.3,3.8, 1])

with col1:
    if os.path.exists(logo1_path):
        st.image(logo1_path, use_container_width=True)
    else:
        st.warning("Logo 1 introuvable")

with col2:
    st.markdown(
        "<h1 style='text-align: center;'>Bilan du Circuit de Vapeur de la Raffinerie</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h4 style='text-align: center; color: gray;'>Réalisée par : <strong>ABDALI Jihane</strong></h4>",
        unsafe_allow_html=True
    )

with col3:
    if os.path.exists(logo2_path):
        st.image(logo2_path, use_container_width=True)
    else:
        st.warning("Logo 2 introuvable")








# Configuration de la page
st.set_page_config(layout="wide")
st.subheader("🧭 Schéma du circuit de vapeur de la raffinerie")

st.info("""👋 **Bienvenue dans l'application de suivi des débits de vapeur du circuit de la raffinerie de COSUMAR**  
Utilisez le menu déroulant pour sélectionner une machine et entrer les données nécessaires.  
L'application calculera automatiquement les bilans thermiques et enregistrera les résultats.
Vous pouvez également télécharger votre rapport sous format PDF.""")


default_image_path = "SCHEMA APP1.png"  # ⚠️ Modifie ce nom si besoin

if os.path.exists(default_image_path):
    image = Image.open(default_image_path)
    # Encodage base64 de l'image pour affichage centré avec HTML
    with open(default_image_path, "rb") as img_file:
        encoded_image = base64.b64encode(img_file.read()).decode()
    
    st.markdown(
        f"""
        <div style='text-align: center;'>
            <img src="data:image/png;base64,{encoded_image}" width="800">
            <p style="font-weight: bold;">📌 Schéma chargé automatiquement</p>
        </div>
        """,
        unsafe_allow_html=True
    )

else:
    st.warning(f"L'image par défaut ({default_image_path}) est introuvable. Veuillez la téléverser manuellement.")
    uploaded_image = st.file_uploader("📤 Téléversez une image du schéma (format .png, .jpg, .jpeg)", type=["png", "jpg", "jpeg"])
    
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, use_container_width=True, caption="📌 Schéma chargé via upload")



date_du_jour = datetime.date.today().strftime('%d/%m/%Y')

st.markdown(f"""
<div style='text-align: left; font-size:22px; font-weight: bold; color: #333;'>
📅 Date : {date_du_jour}
</div>
""", unsafe_allow_html=True)

# Liste des machines
machines = [
    "CEFT 2400", "CEFT 1300", "Bouilleur", "ECH Bouilleur",
    "CEFT 1600","VKT","ECH 2400 (VP1)", 
    "DCH Fondoir F0", "DCH Fondoir F1",  "DCH ES", "ECH EA", "ECH ED", "Condenseur",
    "DCH Fondoir F2","Cuite 710HL", "Cuite 550HL", "Cuite R2", "ECH sécheur","ECH 2400 (VPT)",
    "Cuite R31", "Cuite R32", "Cuite R4", "Cuite A", "Cuite B", "Cuite C", 
    "ECH Commune Carbonatée","Dégraissage de la cuite 710HL","Dégraissage de la cuite 550HL",
    "Dégraissage de la cuite R2","Dégraissage de la cuite A","Dégraissage de la cuite B","Dégraissage de la cuite C",
    "Dégraissage des cuites R31, R32 & R33","Dégraissage des cuites STG1+STG2", "Échappement de la VPT & Gazs incondensables", "Échappement de la VPT & Gazs incondensables des cuites 710HL & R2", "Échappement de la VPT & Gazs incondensables de la cuite 550HL", "Soufflage des filtres"
]

# ---- Fonction Cp ----
def Cp(brix):
    return 4.19 * (brix / 100) + 1.42 * (1 - brix / 100)
                
#------------Densité---------------
def D(brix):
    return 0.96 + brix/200
                
# ---- Bilans ----

def bilan_ceft_2400():
    st.header("Bilan du corps évaporateur à flux tombant 2400 ")
    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, débit volumiques")
    h_VE = st.number_input("Enthalpie VE (KJ/Kg)", min_value=0.0)
    h_CDS = st.number_input("Enthalpie CDS (KJ/Kg)", min_value=0.0)
    h_VP1p = st.number_input("Enthalpie VP1'(KJ/Kg)", min_value=0.0)
    
    Q_SNC = st.number_input("Débit volumique du sirop non concentré SNC entrant (m³/h)", min_value=0.0)
    T_SNC = st.number_input("Température SNC (°C)", min_value=0.0)
    Brix_SNC = st.number_input("Brix SNC (%)", min_value=0.0, max_value=100.0)
    
    T_SC1 = st.number_input("Température du sirop concentré sortant SC1 (°C)", min_value=0.0)
    Brix_SC1 = st.number_input("Brix SC1 (%)", min_value=0.0, max_value=100.0)
    

    if st.button("Calculer VE - CEFT 2400"):
        try:
            Cp_SC1 = Cp(Brix_SC1)
            Cp_SNC = Cp(Brix_SNC)
            Q_SC1 = (Q_SNC*Brix_SNC)/ Brix_SC1
            m_SNC=Q_SNC * D(Brix_SNC)
            m_SC1=(m_SNC * Brix_SNC)/Brix_SC1
            m_VP1p = m_SNC - m_SC1
            numerator = m_VP1p * h_VP1p + m_SC1 * Cp_SC1 * T_SC1 - m_SNC * Cp_SNC * T_SNC
            denominator = h_VE - h_CDS
            if denominator == 0:
                st.error("Division impossible (h_VE = h_CDS)")
                return
            m_VE = numerator / denominator
            m_CDS = m_VE

            st.success(f"🔹Débit vapeur entrante VE calculé = {m_VE:.2f} t/h")
            st.success(f"🔹Débit vapeur sortante VP1 calculé = {m_VP1p:.2f} t/h")
            st.success(f"🔹Débit du sirop sortant SC1 = {Q_SC1:.2f} m³/h = {m_SC1:.2f} t/h" )
            st.success(f"🔹Débit des condensats= {m_CDS:.2f} t/h")

            st.session_state["resultats_machines"]["CEFT 2400"] = {
                "VE": m_VE, "VP1'": m_VP1p, "CDS": m_CDS
            }
        except Exception as e:
            st.error(f"Erreur : {e}")

def bilan_ceft_1300():
    st.header("Bilan du corps évaporateur à flux tombant 1300 ")
    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, débit volumiques")
    h_VE = st.number_input("Enthalpie VE (kJ/kg)", min_value=0.0)
    h_CDS = st.number_input("Enthalpie CDS (kJ/kg)", min_value=0.0)
    h_VP1pp = st.number_input("Enthalpie VP1'' (kJ/kg)", min_value=0.0)
    
    Q_SC1p = st.number_input("Débit du sirop entrant SC1 (m³/h)", min_value=0.0)
    T_SC1p = st.number_input("Température du sirop entrant SC1 (°C)", min_value=0.0)
    Brix_SC1p = st.number_input("Brix du sirop entrant SC1 (%)", min_value=0.0, max_value=100.0)
      
    T_SC2 = st.number_input("Température du sirop concentré sortant SC2 (°C)", min_value=0.0)
    Brix_SC2 = st.number_input("Brix du sirop sortant SC2 (%)", min_value=0.0, max_value=100.0)


    

    if st.button("Calculer VE - CEFT 1300"):
        try:
            Cp_SC1p = Cp(Brix_SC1p)
            Cp_SC2 = Cp(Brix_SC2)
            Q_SC2 = (Q_SC1p*Brix_SC1p)/ Brix_SC2
            m_SC1p=Q_SC1p * D(Brix_SC1p)
            m_SC2=(m_SC1p * Brix_SC1p)/Brix_SC2
            m_VP1pp = m_SC1p - m_SC2
            numerator = m_VP1pp * h_VP1pp + m_SC2 * Cp_SC2 * T_SC2 - m_SC1p * Cp_SC1p * T_SC1p
            denominator = h_VE - h_CDS
            if denominator == 0:
                st.error("Division impossible (h_VE = h_CDS)")
                return
            m_VE = numerator / denominator
            m_CDS = m_VE

            st.success(f"🔹Débit vapeur entrante VE calculé = {m_VE:.2f} t/h")
            st.success(f"🔹Débit vapeur sortante VP1' calculé = {m_VP1pp:.2f} t/h")
            st.success(f"🔹Débit du sirop sortant SC2 = {Q_SC2:.2f} m³/h = {m_SC2:.2f} t/h" ) 
            st.success(f"🔹Débit des condensats = {m_CDS:.2f} t/h")

            st.session_state["resultats_machines"]["CEFT 1300"] = {
                "VE": m_VE, "VP1''": m_VP1pp, "CDS": m_CDS
            }
        except Exception as e:
            st.error(f"Erreur : {e}")

def bilan_bouilleur():
    st.header("Bilan du bouilleur")
    st.info("Saisissez les données des entrées et sorties de votre machine : Enthalpies et les débits volumiques")
    h_VE = st.number_input("Enthalpie VE (kJ/kg)", min_value=0.0)
    m_E = st.number_input("Débit d'eau d'alimentation (t/h)", min_value=0.0)
    T_E = st.number_input("Température de l'eau d'alimentation (kJ/kg)", min_value=0.0)
    h_VPT = st.number_input("Enthalpie VPT (kJ/kg)", min_value=0.0)
    h_P = st.number_input("Enthalpie purge (kJ/kg)", min_value=0.0)
    h_CDS = st.number_input("Enthalpie CDS (kJ/kg)", min_value=0.0)

    if st.button("Calculer VE - Bouilleur"):
        try:
            Brix_E= Brix_CDS =100
            Cp=4.19
            h_E=Cp*T_E
            m_P = 0.02 * m_E
            m_VPT = m_E - m_P
            numerator = m_VPT * h_VPT + m_P * h_P - m_E * h_E
            denominator = h_VE-h_CDS
            if denominator == 0:
                st.error("Division impossible ")
                return
            m_VE = numerator / denominator
           

            st.success(f"🔹Débit vapeur entrante VE calculé = {m_VE:.2f} t/h")
            st.success(f"🔹Débit vapeur sortante VPT calculé = {m_VPT:.2f} t/h")
            st.success(f"🔹Débit de la purge calculé  = {m_P:.2f} t/h")

            st.session_state["resultats_machines"]["Bouilleur"] = {
                "VE": m_VE, "VPT": m_VPT, "Purge": m_P
            }
        except Exception as e:
            st.error(f"Erreur : {e}")





def bilan_echangeur_bouilleur():
    st.header("Bilan de l'échangeur avant bouilleur")

    st.info("Saisissez les données des entrées et sorties de votre machine : Enthalpies et les débits volumiques")

    h_VE = st.number_input("Enthalpie VE (kJ/kg)", min_value=0.0)
    h_CDS = st.number_input("Enthalpie CDS (kJ/kg)", min_value=0.0)
    Q_fe = st.number_input("Débit de l'eau entrant (m³/h))", min_value=0.0)
    Q_fs = st.number_input("Débit de l'eau sortant (m³/h))", min_value=0.0)
    h_fe = st.number_input("Enthalpie de l'eau entrant ", min_value=0.0)
    h_fs = st.number_input("Enthalpie de l'eau sortant ", min_value=0.0)
    h_VE = st.number_input("Enthalpie vapeur entrante VE ", min_value=0.0)
    

    if st.button("Calculer VE - Échangeur Bouilleur"):
        try:
            Brix_fe= Brix_fs =100
            m_fs=Q_fs
            m_fe=Q_fe
            numerator = m_fs * h_fs - m_fe*h_fe
            denominator = h_VE - h_CDS

            if denominator == 0:
                st.error("Division impossible.")
                return

            m_VE = numerator / denominator
            m_CDS = m_VE  # Hypothèse : toute la vapeur se condense

            st.success(f"🔹Débit vapeur entrante VE calculé = {m_VE:.2f} t/h")
            st.success(f"🔹Débit des condensats= {m_CDS:.2f} t/h")

            # Enregistrement des résultats
            st.session_state["resultats_machines"]["ECH Bouilleur"] = {
                "VE": m_VE,
                "CDS": m_CDS
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")


def bilan_ceft_1600():
    st.header("Bilan du corps évaporateur à flux tombant 1600 ")

    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, débit volumiques")

    h_VP1 = st.number_input("Enthalpie vapeur VP1 (kJ/kg)", min_value=0.0)
    h_CDS = st.number_input("Enthalpie condensats (kJ/kg)", min_value=0.0)
    h_VP2 = st.number_input("Enthalpie vapeur VP2 (kJ/kg)", min_value=0.0)

    Q_SC2 = st.number_input("Débit du sirop concentré entrant SC2 (m³/h)", min_value=0.0)
    T_SC2 = st.number_input("Température SC2 (°C)", min_value=0.0)
    Brix_SC2 = st.number_input("Brix SC2 (%)", min_value=0.0, max_value=100.0)

    T_SCf = st.number_input("Température SCf (°C)", min_value=0.0)
    Brix_SCf = st.number_input("Brix SCf (%)", min_value=0.0, max_value=100.0)
    

    
    if st.button("Calculer débit vapeur VP1 - CEFT 1600"):
        try:
            Cp_SC2 = Cp(Brix_SC2)
            Cp_SCf = Cp(Brix_SCf)
            Q_SCf = (Q_SC2*Brix_SC2)/ Brix_SCf
            m_SC2=Q_SC2 * D(Brix_SC2)
            m_SCf=(m_SC2 * Brix_SC2)/Brix_SCf

            m_VP2 = m_SC2 - m_SCf
            numerator = m_VP2 * h_VP2 + m_SCf * Cp_SCf * T_SCf - m_SC2 * Cp_SC2 * T_SC2
            denominator = h_VP1 - h_CDS
            if denominator == 0:
                st.error("Erreur : h_VP1 et h_CDS sont égaux → division impossible.")
                return

            m_VP1 = numerator / denominator
            m_CDS = m_VP1  # Hypothèse : toute la vapeur se condense

            st.success(f"🔹Débit vapeur entrante VP1 calculé = {m_VP1:.2f} t/h")
            st.success(f"🔹Débit vapeur sortante VP2 calculé = {m_VP2:.2f} t/h")
            st.success(f"🔹Débit des condensats= {m_VP1:.2f} t/h")

            # Enregistrement
            st.session_state["resultats_machines"]["CEFT 1600"] = {
                "VP1": m_VP1,
                "VP2": m_VP2,
                "CDS": m_VP1,    
            }        
        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")
######################################################################################
def bilan_vkt():

    st.header("Bilan de la tour de cristallisation VKT")
    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, volume entrant, débit volumiques")
    
    # Enthalpies
    h_VP1 = st.number_input("Enthalpie vapeur VP1 (kJ/kg)", min_value=0.0)
    h_CDS = st.number_input("Enthalpie condensats (kJ/kg)", min_value=0.0)
    h_Eevap = st.number_input("Enthalpie de l'eau évaporée (kJ/kg)", min_value=0.0)

    # Sirop concentré entrant
    Q_SCf = st.number_input("Débit du sirop concentré entrant (m³/h)", min_value=0.0)
    T_SCf = st.number_input("Température du sirop concentré entrant (°C)", min_value=0.0)
    Brix_SCf = st.number_input("Brix du sirop concentré entrant (%)", min_value=0.0, max_value=100.0)

    # Magma entrant
    T_magma = st.number_input("Température du magma entrant (°C)", min_value=0.0)
    Brix_magma = st.number_input("Brix du magma entrant (%)", min_value=0.0, max_value=100.0)

    # Masse cuite sortante
    T_MC = st.number_input("Température de la masse cuite sortante (°C)", min_value=0.0)
    Brix_MC = st.number_input("Brix de la masse cuite sortante (%)", min_value=0.0, max_value=100.0)
    
    if st.button("Calculer débit vapeur VP1 - VKT"):
        try:
            # Capacité calorifique en fonction du Brix
            Cp_SC = Cp(Brix_SCf)
            Cp_MC = Cp(Brix_MC)
            Cp_Magma = Cp(Brix_magma)

            # 1. Masse du sirop concentré entrant
            m_SC = Q_SCf * D(Brix_SCf)

            # 2. Masse du magma entrant (25% du débit SC)
            Q_magma = 0.25 * Q_SCf
            m_Magma = Q_magma * D(Brix_magma)

            # 3. Masse de la masse cuite sortante (formule matière sèche)
            m_MC = (m_SC * Brix_SCf + m_Magma * Brix_magma) / Brix_MC

            # 4. Eau évaporée (bilan matière global)
            m_Eevap = m_SC + m_Magma - m_MC

            # 5. Bilan énergétique pour m_VP1 (formule corrigée)
            numerator = (
                m_Eevap * h_Eevap
                + m_MC * Cp_MC * T_MC
                - m_Magma * Cp_Magma * T_magma
                - m_SC * Cp_SC * T_SCf
            )
            denominator = h_VP1 - h_CDS
            if denominator == 0:
                st.error("Erreur : h_VP1 et h_CDS sont égaux → division impossible.")
                return

            m_VP1 = numerator / denominator
            m_CDS = m_VP1  # Hypothèse : condensation totale

            # Résultats
            st.success(f"🔹Débit vapeur entrante VP1 calculé = {m_VP1:.2f} t/h")
            st.success(f"🔹Débit des condensats = {m_CDS:.2f} t/h")
            st.success(f"🔹Débit de l'eau évaporée calculé = {m_Eevap:.2f} t/h")
            st.success(f"🔹Débit masse cuite sortante = {m_MC:.2f} t/h")

            # Sauvegarde dans la session
            st.session_state["resultats_machines"]["VKT"] = {
                "VP1": m_VP1,
                "CDS": m_CDS,
                "Eau évaporée": m_Eevap,
                "Masse cuite": m_MC,
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")

####################################################################

def bilan_echangeur_2400_VP1():
    st.header("Bilan de l'échangeur 2400 pour la vapeur VP1 ")
    st.info("Saisissez les données des entrées et sorties de votre machine : Enthalpies, Températures, Brix ")
    
        # Saisie des paramètres

    T_Vtot = st.number_input("Température de la vapeur totale entrante (°C)", min_value=0.0)
    h_Vtot = st.number_input("Enthalpie  de la vapeur totale entrante (kJ/kg)", min_value=0.0)
    h_CDStot = st.number_input("Enthalpie des condensats  de la vapeur totale entrante (kJ/kg)", min_value=0.0)

    T_SNC = st.number_input("Température du sirop non chauffé entrant (°C)", min_value=0.0)
    Brix_SNC = st.number_input("Brix  du sirop non chauffé entrant  (%)", min_value=0.0)
    Q_SNC=  st.number_input("Débit du sirop non chauffé entrant (m³/h)", min_value=0.0)

    T_SC = st.number_input("Température du sirop chauffé sortant (°C)", min_value=0.0)
    Brix_SC = st.number_input("Brix du sirop chauffé sortant (%)", min_value=0.0)
    Q_SC=  st.number_input("Débit du sirop chauffé sortant (m³/h)", min_value=0.0)

    # Calcul du débit massique de vapeur
    if st.button("Calculer débit vapeur totale - ECH 2400 (VP1)"):
        try:
            Cp_SC = Cp(Brix_SC)
            Cp_SNC = Cp(Brix_SNC)
            D_SC= D(Brix_SC)
            D_SNC= D(Brix_SNC)
            m_SC=Q_SC*D_SC
            m_SNC=Q_SNC*D_SNC

            numerator = m_SC * Cp_SC * T_SC - m_SNC * Cp_SNC * T_SNC
            denominator = h_Vtot - h_CDStot
            if denominator == 0:
                st.error("Erreur : h_Vptot et h_CDS sont égaux → division impossible.")
                return

            m_Vtot = numerator / denominator
            m_CDS = m_Vtot  # Hypothèse : condensation totale
    
            st.success(f"🔹Débit vapeur entrante calculé = {m_Vtot:.2f} t/h")
            st.success(f"🔹Débit des condensats = {m_Vtot:.2f} t/h")
            st.success(f"🔹Débit VP1 calculé = { m_Vtot*0.75:.2f} t/h")
            st.success(f"🔹Débit des condensats (VP1) = { m_Vtot*0.75:.2f} t/h")
            # Enregistrement des résultats
            st.session_state["resultats_machines"]["ECH 2400 (VP1)"] = {
                "VP1": m_Vtot*0.75,
                "CDS(VP1)": m_Vtot*0.75,
            }
        except ZeroDivisionError:
            st.error("Erreur de division par zéro dans le calcul du logarithme.")
        except Exception as e:
            st.error(f"Erreur inattendue : {e}")

#########################################################################################################


#################################################################################################################""
def bilan_dch_f0():
    st.header("Bilan du DCH du fondoir F0")
    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, débit volumiques")
    h_VP2 = st.number_input("Enthalpie vapeur VP2 (kJ/kg)", min_value=0.0)
    Q_Memp = st.number_input("Débit du sirop non concentré sortie de l'empateur (m³/h)", min_value=0.0)
    T_Memp = st.number_input("Température du sirop non concentré sortie de l'empateur (°C)", min_value=0.0)
    Brix_Memp = st.number_input("Brix du sirop non concentré sortie de l'empateur (%)", min_value=0.0, max_value=100.0)

    Q_MF0 = st.number_input("Débit du sirop sortant vers F0 (m³/h)", min_value=0.0)
    T_MF0 = st.number_input("Température du sirop sortant vers F0 (°C)", min_value=0.0)
    Brix_MF0 = st.number_input("Brix du sirop sortant vers F0 (%)", min_value=0.0, max_value=100.0)


    if st.button("Calculer VP2 - DCH F0"):
        try:
            Cp_Memp = Cp(Brix_Memp)
            Cp_MF0 = Cp(Brix_MF0)
            m_Memp=Q_Memp* D(Brix_Memp)
            m_MF0 = Q_MF0* D(Brix_MF0)
            numerator = m_MF0 * Cp_MF0 * T_MF0 - m_Memp * Cp_Memp * T_Memp
            denominator = h_VP2

            if denominator == 0:
                st.error("Erreur : enthalpie vapeur VP2 = 0 → division impossible.")
                return

            m_VP2 = numerator / denominator

            st.success(f"🔹Débit vapeur entrante VP2 calculé = {m_VP2:.2f} t/h")

            # Enregistrement dans session_state
            st.session_state["resultats_machines"]["DCH Fondoir F0"] = {
                "VP2": m_VP2
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")


##################################################################

def bilan_dch_f1():
    st.header("Bilan du DCH du fondoir F1")
    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, débit volumiques")

    h_VP2 = st.number_input("Enthalpie vapeur VP2 (kJ/kg)", min_value=0.0)

    Q_MF0 = st.number_input("Débit du sirop sortant de F0 (m³/h)", min_value=0.0)
    T_MF0 = st.number_input("Température du sirop sortant de F0 (°C)", min_value=0.0)
    Brix_MF0 = st.number_input("Brix du sirop sortant de F0 (%)", min_value=0.0, max_value=100.0)

    Q_MF1 = st.number_input("Débit du sirop sortant vers F1 (m³/h)", min_value=0.0)
    T_MF1 = st.number_input("Température du sirop sortant vers F1 (°C)", min_value=0.0)
    Brix_MF1 = st.number_input("Brix du sirop sortant vers F1 (%)", min_value=0.0, max_value=100.0)


    if st.button("Calculer VP2 - DCH F1"):
        try:
            Cp_MF0= Cp(Brix_MF0)
            Cp_MF1 = Cp(Brix_MF1)
            m_MF0= Q_MF0* D(Brix_MF0)
            m_MF1 = Q_MF1* D(Brix_MF1)
            numerator = (m_MF1 * Cp_MF1 * T_MF1) - (m_MF0 * Cp_MF0 * T_MF0)
            denominator = h_VP2

            if denominator == 0:
                st.error("Erreur : enthalpie vapeur VP2 = 0 → division impossible.")
                return

            m_VP2 = numerator / denominator

            st.success(f"🔹Débit vapeur entrante VP2 calculé = {m_VP2:.2f} t/h")

            # Enregistrement dans session_state
            st.session_state["resultats_machines"]["DCH Fondoir F1"] = {
                "VP2": m_VP2
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")




def bilan_dch_ES():
    st.header("Bilan du DCH du fondoir des eaux sucrées")
    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, débit volumiques")

    h_VP2 = st.number_input("Enthalpie vapeur VP2 (kJ/kg)", min_value=0.0)

    Q_ESe = st.number_input("Débit des eaux sucrées entrantes (m³/h)", min_value=0.0)
    T_ESe = st.number_input("Température des eaux sucrées entrantes (°C)", min_value=0.0)
    Brix_ESe = st.number_input("Brix des eaux sucrées entrantes (%)", min_value=0.0, max_value=100.0)

    Q_ESs = st.number_input("Débit des eaux sucrées sortantes (m³/h)", min_value=0.0)
    T_ESs = st.number_input("Température des eaux sucrées sortantes (°C)", min_value=0.0)
    Brix_ESs = st.number_input("Brix des eaux sucrées sortantes (%)", min_value=0.0, max_value=100.0)

    h_CDS = st.number_input("Enthalpie des condensats (kJ/kg)", min_value=0.0)


    if st.button("Calculer VP2 - DCH ES"):
        try:
            Cp_ESs = Cp(Brix_ESs)
            Cp_ESe = Cp(Brix_ESe)
            m_ESe= Q_ESe* D(Brix_ESe)
            m_ESs = Q_ESs* D(Brix_ESs)

            numerator = m_ESs * Cp_ESs * T_ESs - m_ESe * Cp_ESe * T_ESe
            denominator = h_VP2 - h_CDS

            if denominator == 0:
                st.error("Erreur : enthalpie vapeur VP2 = 0 → division impossible.")
                return

            m_VP2 = numerator / denominator
            m_CDS = m_VP2

            st.success(f"🔹Débit vapeur entrante VP2 calculé = {m_VP2:.2f} t/h")

            # Enregistrement dans session_state
            st.session_state["resultats_machines"]["DCH ES"] = {
                "VP2": m_VP2,
                "CDS": m_CDS
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")

########################################################################
def bilan_echangeur_EA():
    st.header("Bilan de l'échangeur des eaux adoucies ")
    st.info("Saisissez les données des entrées et sorties de votre machine : Enthalpies, Températures, Brix ")
    
        # Saisie des paramètres

    T_VP2 = st.number_input("Température de la VP2 entrante (°C)", min_value=0.0)
    h_VP2 = st.number_input("Enthalpie  de la VP2 entrante (kJ/kg)", min_value=0.0)
    h_CDS = st.number_input("Enthalpie des condensats la VP2 entrante (kJ/kg)", min_value=0.0)

    T_ee = st.number_input("Température de l'eau entrante (°C)", min_value=0.0)
    Q_ee=  st.number_input("Débit de l'eau entrante (m³/h)", min_value=0.0)

    T_es = st.number_input("Température de l'eau adoucie sortante (°C)", min_value=0.0)
    Q_es=  st.number_input("Débit de l'eau adoucie sortante (m³/h)", min_value=0.0)

    # Calcul du débit massique de vapeur
    if st.button("Calculer débit vapeur totale - ECH EA"):
        try:
            Cp_eau =4.19
            D_eau= D(100)
            m_ee=Q_ee*D_eau
            m_es=Q_es*D_eau

            numerator = m_es * Cp_eau* T_es - m_ee * Cp_eau * T_ee
            denominator = h_VP2 - h_CDS
            if denominator == 0:
                st.error("Erreur : h_VP2 et h_CDS sont égaux → division impossible.")
                return

            m_VP2 = numerator / denominator
            m_CDS = m_VP2  # Hypothèse : condensation totale
    
            st.success(f"🔹Débit VP2 calculé = { m_VP2:.2f} t/h")
            st.success(f"🔹Débit des condensats = { m_VP2:.2f} t/h")
            # Enregistrement des résultats
            st.session_state["resultats_machines"]["ECH EA"] = {
                "VP2":m_VP2,
                "CDS": m_VP2,
            }
        except ZeroDivisionError:
            st.error("Erreur de division par zéro dans le calcul du logarithme.")
        except Exception as e:
            st.error(f"Erreur inattendue : {e}")
        
##################################################################################

def bilan_echangeur_ED():
    st.header("Bilan de l'échangeur des eaux déminéralisées ")
    st.info("Saisissez les données des entrées et sorties de votre machine : Enthalpies, Températures, Brix ")
    
        # Saisie des paramètres

    T_VP2 = st.number_input("Température de la VP2 entrante (°C)", min_value=0.0)
    h_VP2 = st.number_input("Enthalpie  de la VP2 entrante (kJ/kg)", min_value=0.0)
    h_CDS = st.number_input("Enthalpie des condensats la VP2 entrante (kJ/kg)", min_value=0.0)

    T_ee = st.number_input("Température de l'eau entrante (°C)", min_value=0.0)
    Q_ee=  st.number_input("Débit de l'eau entrante (m³/h)", min_value=0.0)

    T_es = st.number_input("Température de l'eau déminéralisée sortante (°C)", min_value=0.0)
    Q_es=  st.number_input("Débit de l'eau déminéralisée sortante (m³/h)", min_value=0.0)

    # Calcul du débit massique de vapeur
    if st.button("Calculer débit vapeur totale - ECH ED"):
        try:
            Cp_eau =4.19
            D_eau= D(100)
            m_ee=Q_ee*D_eau
            m_es=Q_es*D_eau

            numerator = m_es * Cp_eau* T_es - m_ee * Cp_eau * T_ee
            denominator = h_VP2 - h_CDS
            if denominator == 0:
                st.error("Erreur : h_VP2 et h_CDS sont égaux → division impossible.")
                return

            m_VP2 = numerator / denominator
            m_CDS = m_VP2  # Hypothèse : condensation totale
    
            st.success(f"🔹Débit VP2 calculé = { m_VP2:.2f} t/h")
            st.success(f"🔹Débit des condensats = { m_VP2:.2f} t/h")
            # Enregistrement des résultats
            st.session_state["resultats_machines"]["ECH ED"] = {
                "VP2":m_VP2,
                "CDS": m_VP2,
            }
        except ZeroDivisionError:
            st.error("Erreur de division par zéro dans le calcul du logarithme.")
        except Exception as e:
            st.error(f"Erreur inattendue : {e}")


###########################################################################
def bilan_condenseur():
    st.header("Bilan du Condenseur")
    st.info("Le débit de vapeur au condenseur est estimé par différence entre la vapeur générée (par CEFT 1600) et celle consommée par les DCH.")

    try:
        resultats = st.session_state.get("resultats_machines", {})

        # Vapeur produite par la CEFT 1600 (VP2)
        VP2_CEFT = resultats.get("CEFT 1600", {}).get("VP2", 0)

        # Vapeurs consommées par les DCHs
        VP2_F0 = resultats.get("DCH Fondoir F0", {}).get("VP2", 0)
        VP2_F1 = resultats.get("DCH Fondoir F1", {}).get("VP2", 0)
        VP2_ES = resultats.get("DCH ES", {}).get("VP2", 0)
        VP2_EA = resultats.get("ECH EA", {}).get("VP2", 0)
        VP2_ED = resultats.get("ECH ED", {}).get("VP2", 0)

        vapeur_consommée =  VP2_F0 + VP2_F1 + VP2_ES + VP2_EA+ VP2_ED
        vapeur_condenseur = VP2_CEFT - vapeur_consommée

        # Affichage
        st.write(f"🔸 Vapeur CEFT 1600 (VP2) = {VP2_CEFT:.2f} t/h")
        st.write(f"🔸 Vapeur consommée par DCHs et échangeurs = {vapeur_consommée:.2f} t/h")
        st.success(f"🔹 Débit de vapeur arrivant au condenseur = {vapeur_condenseur:.2f} t/h")

        # Enregistrement
        st.session_state["resultats_machines"]["Condenseur"] = {
            "VP2": vapeur_condenseur
        }

        if abs(vapeur_condenseur) < 0.1:
            st.warning("💡 Le débit est très faible, ce qui confirme que toute la vapeur a été consommée.")

    except Exception as e:
        st.error(f"Erreur dans le calcul du condenseur : {e}")


##########################################################################
def bilan_dch_f2():
    st.header("Bilan du DCH du fondoir F2")
    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, débit volumiques")
    h_VPT = st.number_input("Enthalpie vapeur VPT (kJ/kg)", min_value=0.0)
    Q_MF1 = st.number_input("Débit du sirop sortant de F1 (m³/h)", min_value=0.0)
    T_MF1 = st.number_input("Température du sirop sortant de F1 (°C)", min_value=0.0)
    Brix_MF1 = st.number_input("Brix du sirop sortant de F1 (%)", min_value=0.0, max_value=100.0)

    Q_MF2 = st.number_input("Débit du sirop sortant vers F2 (m³/h)", min_value=0.0)
    T_MF2 = st.number_input("Température du sirop sortant vers F2 (°C)", min_value=0.0)
    Brix_MF2 = st.number_input("Brix du sirop sortant vers F2 (%)", min_value=0.0, max_value=100.0)


    if st.button("Calculer VP2 - DCH F2"):
        try:
            Cp_MF1 = Cp(Brix_MF1)
            Cp_MF2 = Cp(Brix_MF2)
            m_MF2=Q_MF2* D(Brix_MF2)
            m_MF1 = Q_MF1* D(Brix_MF1)
            numerator = m_MF2 * Cp_MF2 * T_MF2 - m_MF1 * Cp_MF1 * T_MF1
            denominator = h_VPT

            if denominator == 0:
                st.error("Erreur : enthalpie vapeur VP2 = 0 → division impossible.")
                return

            m_VPT = numerator / denominator

            st.success(f"🔹Débit vapeur entrante VPT calculé = {m_VPT:.2f} t/h")

            # Enregistrement dans session_state
            st.session_state["resultats_machines"]["DCH Fondoir F2"] = {
                "VPT": m_VPT
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")
#############################################################################

def bilan_cuite710():
    st.header("Bilan de la cuite 710 HL")
    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, volume entrant, débit volumiques")

    h_VPT = st.number_input("Enthalpie vapeur VPT (kJ/kg)", min_value=0.0)
    h_CDS = st.number_input("Enthalpie des condensats (kJ/kg)", min_value=0.0)
    h_Eevap = st.number_input("Enthalpie de l'eau évaporée (kJ/kg)", min_value=0.0)

    T_SC = st.number_input("Température du sirop concentré entrant (°C)", min_value=0.0)
    Brix_SC = st.number_input("Brix du sirop concentré entrant (%)", min_value=0.0, max_value=100.0)

    V_MC = st.number_input("Volume sortant de la masse cuite (m³)", min_value=0.0)
    T_MC = st.number_input("Température de la masse cuite (°C)", min_value=0.0)
    Brix_MC = st.number_input("Brix de la masse cuite (%)", min_value=0.0, max_value=100.0)


   

    if st.button("Calculer VPT - Cuite 710HL"):
        try:
            Cp_SC = Cp(Brix_SC)
            Cp_MC = Cp(Brix_MC)
            D_SC = D(Brix_SC)
            D_MC = D(Brix_MC)

        # Le bilan matière
            V_SC = (D_MC * V_MC * Brix_MC)/(D_SC * Brix_SC)
            m_SC = D_SC * V_SC * (Brix_SC)/100
            m_MC = D_MC * V_MC * (Brix_MC)/100
            m_Eevap = V_SC - V_MC


            numerator = m_Eevap * h_Eevap + V_MC * Cp_MC * T_MC - V_SC * Cp_SC * T_SC
            denominator = h_VPT - h_CDS

            if denominator == 0:
                st.error("Erreur : h_VPT et h_CDS sont égaux → division impossible.")
                return

            m_VPT = numerator / denominator
            m_CDS = m_VPT  # Hypothèse : condensation totale

            st.success(f"🔹Débit vapeur entrante VPT calculé = {m_VPT:.2f} t/h")
            st.success(f"🔹Débit des condensats = {m_CDS:.2f} t/h")
            st.success(f"🔹Débit de l'eau évaporée calculé = {m_Eevap:.2f} t/h")
            st.success(f"🔹Volume du sirop entrant calculé = {V_SC:.2f} m³")

            st.session_state["resultats_machines"]["Cuite 710HL"] = {
                "VPT": m_VPT,
                "CDS": m_CDS,
                "Eau évaporée": m_Eevap,
                "Volume entrant du sirop" : V_SC

            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")

def bilan_cuite550():
    st.header("Bilan de la cuite 550 HL")
    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, volume entrant, débit volumiques")

    h_VPT = st.number_input("Enthalpie vapeur VPT (kJ/kg)", min_value=0.0)
    h_CDS = st.number_input("Enthalpie des condensats (kJ/kg)", min_value=0.0)
    h_Eevap = st.number_input("Enthalpie de l'eau évaporée (kJ/kg)", min_value=0.0)

    T_SC = st.number_input("Température du sirop concentré entrant (°C)", min_value=0.0)
    Brix_SC = st.number_input("Brix du sirop concentré entrant (%)", min_value=0.0, max_value=100.0)

    V_MC = st.number_input("Volume sortant de la masse cuite (m³)", min_value=0.0)
    T_MC = st.number_input("Température de la masse cuite (°C)", min_value=0.0)
    Brix_MC = st.number_input("Brix de la masse cuite (%)", min_value=0.0, max_value=100.0)

   

    if st.button("Calculer VPT - Cuite 550HL"):
        try:
            Cp_SC = Cp(Brix_SC)
            Cp_MC = Cp(Brix_MC)
            D_SC = D(Brix_SC)
            D_MC = D(Brix_MC)

        # Le bilan matière
            V_SC = (D_MC * V_MC * Brix_MC)/(D_SC * Brix_SC)
            m_SC = D_SC * V_SC * (Brix_SC)/100
            m_MC = D_MC * V_MC * (Brix_MC)/100
            m_Eevap = V_SC - V_MC


            numerator = m_Eevap * h_Eevap + V_MC * Cp_MC * T_MC - V_SC * Cp_SC * T_SC
            denominator = h_VPT - h_CDS

            if denominator == 0:
                st.error("Erreur : h_VPT et h_CDS sont égaux → division impossible.")
                return

            m_VPT = numerator / denominator
            m_CDS = m_VPT  # Hypothèse : condensation totale

            st.success(f"🔹Débit vapeur entrante VPT calculé = {m_VPT:.2f} t/h")
            st.success(f"🔹Débit des condensats = {m_CDS:.2f} t/h")
            st.success(f"🔹Débit de l'eau évaporée calculé = {m_Eevap:.2f} t/h")
            st.success(f"🔹Volume du sirop entrant calculé = {V_SC:.2f} m³")


            st.session_state["resultats_machines"]["Cuite 550HL"] = {
                "VPT": m_VPT,
                "CDS": m_CDS,
                "Eau évaporée": m_Eevap,
                "Volume entrant du sirop" : V_SC

            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")


def bilan_cuiteR2():
    st.header("Bilan de la cuite R2")
    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, volume entrant, débit volumiques")

    h_VPT = st.number_input("Enthalpie vapeur VPT (kJ/kg)", min_value=0.0)
    h_CDS = st.number_input("Enthalpie des condensats (kJ/kg)", min_value=0.0)
    h_Eevap = st.number_input("Enthalpie de l'eau évaporée (kJ/kg)", min_value=0.0)

    T_SC = st.number_input("Température du sirop concentré entrant (°C)", min_value=0.0)
    Brix_SC = st.number_input("Brix du sirop concentré entrant (%)", min_value=0.0, max_value=100.0)

    V_MC = st.number_input("Volume sortant de la masse cuite (m³)", min_value=0.0)
    T_MC = st.number_input("Température de la masse cuite (°C)", min_value=0.0)
    Brix_MC = st.number_input("Brix de la masse cuite (%)", min_value=0.0, max_value=100.0)

   

    if st.button("Calculer VPT - Cuite R2"):
        try:
            Cp_SC = Cp(Brix_SC)
            Cp_MC = Cp(Brix_MC)
            D_SC = D(Brix_SC)
            D_MC = D(Brix_MC)

        # Le bilan matière
            V_SC = (D_MC * V_MC * (Brix_MC/100))/(D_SC * (Brix_SC/100))
            m_SC = D_SC * V_SC * (Brix_SC)/100
            m_MC = D_MC * V_MC * (Brix_MC)/100
            m_Eevap = V_SC - V_MC


            numerator = m_Eevap * h_Eevap + V_MC * Cp_MC * T_MC - V_SC * Cp_SC * T_SC
            denominator = h_VPT - h_CDS

            if denominator == 0:
                st.error("Erreur : h_VPT et h_CDS sont égaux → division impossible.")
                return

            m_VPT = numerator / denominator
            m_CDS = m_VPT  # Hypothèse : condensation totale

            st.success(f"🔹Débit vapeur entrante VPT calculé = {m_VPT:.2f} t/h")
            st.success(f"🔹Débit des condensats = {m_CDS:.2f} t/h")
            st.success(f"🔹Débit de l'eau évaporée calculé = {m_Eevap:.2f} t/h")
            st.success(f"🔹Volume du sirop entrant calculé = {V_SC:.2f} t/h")


            st.session_state["resultats_machines"]["Cuite R2"] = {
                "VPT": m_VPT,
                "CDS": m_CDS,
                "Eau évaporée": m_Eevap,
                "Volume entrant du sirop" : V_SC

            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")

###############################################################
def bilan_echangeur_2400_VPT():
        st.header("Bilan de l'échangeur 2400 pour la vapeur VPT")
        st.info("Saisissez les données des entrées et sorties de votre machine : Enthalpies, Températures, Brix ")
        T_Vtot = st.number_input("Température de la vapeur totale entrante (°C)", min_value=0.0)
        h_Vtot = st.number_input("Enthalpie  de la vapeur totale entrante (kJ/kg)", min_value=0.0)
        h_CDStot = st.number_input("Enthalpie des condensats  de la vapeur totale entrante (kJ/kg)", min_value=0.0)

        T_SC = st.number_input("Température du sirop non chauffé entrant (°C)", min_value=0.0)
        Brix_SC = st.number_input("Brix  du sirop non chauffé entrant  (%)", min_value=0.0)
        Q_SC=  st.number_input("Débit du sirop non chauffé entrant (m³/h)", min_value=0.0)

        T_SNC = st.number_input("Température du sirop chauffé sortant (°C)", min_value=0.0)
        Brix_SNC = st.number_input("Brix du sirop chauffé sortant (%)", min_value=0.0)
        Q_SNC=  st.number_input("Débit du sirop chauffé sortant (m³/h)", min_value=0.0)

        # Saisie des paramètreS
    
    # Calcul du débit massique de vapeur
        if st.button("Calculer débit vapeur totale - ECH 2400 (VPT)"):
            try:
                Cp_SC = Cp(Brix_SC)
                Cp_SNC = Cp(Brix_SNC)
                D_SC= D(Brix_SC)
                D_SNC= D(Brix_SNC)
                m_SC=Q_SC*D_SC
                m_SNC=Q_SNC*D_SNC

                numerator = m_SC * Cp_SC * T_SC - m_SNC * Cp_SNC * T_SNC
                denominator = -h_Vtot+h_CDStot
                if denominator == 0:
                    st.error("Erreur : h_Vptot et h_CDS sont égaux → division impossible.")
                    return

                m_Vtot = numerator / denominator
                m_CDS = m_Vtot  # Hypothèse : condensation totale
        
                st.success(f"🔹Débit vapeur entrante calculé = {m_Vtot:.2f} t/h")
                st.success(f"🔹Débit des condensats = {m_Vtot:.2f} t/h")
                st.success(f"🔹Débit VPT calculé = { m_Vtot*0.25:.2f} t/h")
                st.success(f"🔹Débit des condensats (VPT) = { m_Vtot*0.25:.2f} t/h")
                # Enregistrement des résultats
                st.session_state["resultats_machines"]["ECH 2400 (VPT)"] = {
                    "VPT": m_Vtot*0.25,
                    "CDS(VPT)": m_Vtot*0.25,
                }
            except ZeroDivisionError:
                st.error("Erreur de division par zéro dans le calcul du logarithme.")
            except Exception as e:
                st.error(f"Erreur inattendue : {e}")
###################################################################
def bilan_ECH_sécheur():
    st.header("Bilan de l'échangeur sécheur")
    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, débit volumiques")

    h_VPT = st.number_input("Enthalpie vapeur VPT (kJ/kg)", min_value=0.0)

    m_SHe = st.number_input("Débit du sucre non séché (m³/h)", min_value=0.0)
    T_SHe = st.number_input("Température du sucre non séché (°C)", min_value=0.0)
    Brix_SHe = st.number_input("Brix du sucre non séché (%)", min_value=0.0, max_value=100.0, value=100.0)

    m_SHs = st.number_input("Débit du sucre séché (m³/h)", min_value=0.0)
    T_SHs = st.number_input("Température du sucre séché (°C)", min_value=0.0)
    Brix_SHs = st.number_input("Brix du sucre séché (%)", min_value=0.0, max_value=100.0, value=100.0)

    h_CDS = st.number_input("Enthalpie des condensats (kJ/kg)", min_value=0.0)


    if st.button("Calculer VPT - ECH Sécheur"):
        try:
            Cp_SHs = Cp(Brix_SHs)
            Cp_SHe = Cp(Brix_SHe)

            numerator = m_SHs * Cp_SHs * T_SHs - m_SHe * Cp_SHe * T_SHe
            denominator = h_VPT - h_CDS

            if denominator == 0:
                st.error("Erreur : enthalpie vapeur VPT = 0 → division impossible.")
                return

            m_VPT = numerator / denominator
            m_CDS = m_VPT

            st.success(f"🔹Débit vapeur entrante VPT calculé = {m_VPT:.2f} t/h")

            # Enregistrement dans session_state
            st.session_state["resultats_machines"]["ECH sécheur"] = {
                "VPT": m_VPT,
                "CDS": m_CDS
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")

###############################################################################33


def bilan_cuiteR31():
    st.header("Bilan de la cuite R31")
    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, volume entrant, débit volumiques")

    h_VPc = st.number_input("Enthalpie de la vapeur compressée (kJ/kg)", min_value=0.0)
    h_CDS = st.number_input("Enthalpie des condensats (kJ/kg)", min_value=0.0)
    h_Eevap = st.number_input("Enthalpie de l'eau évaporée (kJ/kg)", min_value=0.0)

    T_MCvkt =st.number_input("Température de la masse cuite entrante issue de la VKT(°C)", min_value=0.0)
    Brix_MCvkt = st.number_input("Brix de la masse cuite issue de la VKT (%)", min_value=0.0, max_value=100.0)

    V_MCs = st.number_input("Volume de la masse cuite sortante MCs (m³)", min_value=0.0)
    T_MCs = st.number_input("Température de la masse cuite sortante MCs (°C)", min_value=0.0)
    Brix_MCs = st.number_input("Brix de la masse cuite sortante MCs (%)", min_value=0.0, max_value=100.0)


    if st.button("Calculer VPc - Cuite R31"):
        try:
            Cp_MCvkt = Cp(Brix_MCvkt)
            Cp_MCs = Cp(Brix_MCs)
            D_MCvkt = D(Brix_MCvkt)
            D_MCs = D(Brix_MCs)

            # Bilan matière
            V_MCvkt = (D_MCs * V_MCs * (Brix_MCs / 100)) /(D_MCvkt * (Brix_MCvkt / 100))
            m_MCvkt = D_MCvkt * V_MCvkt * (Brix_MCvkt / 100)
            m_MCs = D_MCs * V_MCs * (Brix_MCs / 100)
            m_Eevap = V_MCvkt - V_MCs

            # Bilan énergétique
            numerator = m_Eevap * h_Eevap + V_MCs * Cp_MCs * T_MCs - V_MCvkt * Cp_MCvkt * T_MCvkt
            denominator = h_VPc - h_CDS

            if denominator == 0:
                st.error("Erreur : h_VPc et h_CDS sont égaux → division impossible.")
                return

            m_VPc = numerator / denominator
            m_CDS = m_VPc  # Hypothèse : condensation totale

            st.success(f"🔹Débit vapeur entrante VPc calculé = {m_VPc:.2f} t/h")
            st.success(f"🔹Débit des condensats = {m_CDS:.2f} t/h")
            st.success(f"🔹Débit de l'eau évaporée calculé = {m_Eevap:.2f} t/h")
            st.success(f"🔹Volume de la masse cuite entrante calculé = {V_MCvkt:.2f} t/h")


            st.session_state["resultats_machines"]["Cuite R31"] = {
                "Vvkt": m_VPc,
                "CDS": m_CDS,
                "Eau évaporée": m_Eevap,
                "Volume entrant de la masse cuite": V_MCvkt
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")



def bilan_cuiteR32():
    st.header("Bilan de la cuite R32")
    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, volume entrant, débit volumiques")

    h_VPc = st.number_input("Enthalpie de la vapeur compressée (kJ/kg)", min_value=0.0)
    h_CDS = st.number_input("Enthalpie des condensats (kJ/kg)", min_value=0.0)
    h_Eevap = st.number_input("Enthalpie de l'eau évaporée (kJ/kg)", min_value=0.0)

    T_MCR31 = st.number_input("Température de la masse cuite issue de la cuite R31 (°C)", min_value=0.0)
    Brix_MCR31 = st.number_input("Brix de la masse cuite issue de la R31 (%)", min_value=0.0, max_value=100.0)

    V_MCR32 = st.number_input("Volume de la masse cuite sortante (m³)", min_value=0.0)
    T_MCR32 = st.number_input("Température de la masse cuite sortante (°C)", min_value=0.0)
    Brix_MCR32 = st.number_input("Brix de la masse cuite sortante (%)", min_value=0.0, max_value=100.0)


    if st.button("Calculer VPc - Cuite R32"):
        try:
            Cp_MCR31 = Cp(Brix_MCR31)
            Cp_MCR32 = Cp(Brix_MCR32)
            D_MCR31 = D(Brix_MCR31)
            D_MCR32 = D(Brix_MCR32)

            # Bilan matière
            V_MCR31 = (D_MCR32 * V_MCR32 * (Brix_MCR32 / 100)) /(D_MCR31 * (Brix_MCR31 / 100))
            m_MCR31 = D_MCR31 * V_MCR31 * (Brix_MCR31 / 100)
            m_MCR32 = D_MCR32 * V_MCR32 * (Brix_MCR32 / 100)
            m_Eevap = V_MCR31 - V_MCR32

            # Bilan énergétique
            numerator = m_Eevap * h_Eevap + V_MCR32 * Cp_MCR32 * T_MCR32 - V_MCR31 * Cp_MCR31 * T_MCR31
            denominator = h_VPc - h_CDS

            if denominator == 0:
                st.error("Erreur : h_VPc et h_CDS sont égaux → division impossible.")
                return

            m_VPc = numerator / denominator
            m_CDS = m_VPc  # Hypothèse : condensation totale

            st.success(f"🔹 Débit vapeur VPc estimé : {m_VPc:.2f} t/h")
            st.success(f"🔹Eau évaporée = {m_Eevap:.2f} t/h")
            st.success(f"🔹Volume entrant = {V_MCR31:.2f} t/h")
            st.success(f"🔹Condensats = {m_CDS:.2f} t/h")

            st.session_state["resultats_machines"]["Cuite R32"] = {
                "Vvkt": m_VPc,
                "CDS": m_CDS,
                "Eau évaporée": m_Eevap,
                "Volume entrant de la masse cuite": V_MCR31
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")


def bilan_cuiteR4():
    st.header("Bilan de la cuite R4")
    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, volume entrant, débit volumiques")

    h_VPc = st.number_input("Enthalpie de la vapeur compressée (kJ/kg)", min_value=0.0)
    h_CDS = st.number_input("Enthalpie des condensats (kJ/kg)", min_value=0.0)
    h_Eevap = st.number_input("Enthalpie de l'eau évaporée (kJ/kg)", min_value=0.0)

    T_MCR32 = st.number_input("Température de la masse cuite issue de la cuite R32 (°C)", min_value=0.0)
    Brix_MCR32 = st.number_input("Brix de la masse cuite issue de la R32 (%)", min_value=0.0, max_value=100.0)

    V_MCR4 = st.number_input("Volume de la masse cuite sortante (m³)", min_value=0.0)
    T_MCR4 = st.number_input("Température de la masse cuite sortante (°C)", min_value=0.0)
    Brix_MCR4 = st.number_input("Brix de la masse cuite sortante (%)", min_value=0.0, max_value=100.0)

    if st.button("Calculer VPc - Cuite R4"):
        try:
            Cp_MCR32 = Cp(Brix_MCR32)
            Cp_MCR4 = Cp(Brix_MCR4)
            D_MCR32 = D(Brix_MCR32)
            D_MCR4 = D(Brix_MCR4)

            # Bilan matière
            V_MCR32 = (D_MCR4 * V_MCR4 * (Brix_MCR4 / 100)) /(D_MCR32 * (Brix_MCR32 / 100))
            m_MCR32 = D_MCR32 * V_MCR32 * (Brix_MCR32 / 100)
            m_MCR4 = D_MCR4 * V_MCR4 * (Brix_MCR4 / 100)
            m_Eevap = V_MCR32 - V_MCR4

            # Bilan énergétique
            numerator = m_Eevap * h_Eevap + V_MCR4 * Cp_MCR4 * T_MCR4 - V_MCR32 * Cp_MCR32 * T_MCR32
            denominator = h_VPc - h_CDS

            if denominator == 0:
                st.error("Erreur : h_VPc et h_CDS sont égaux → division impossible.")
                return

            m_VPc = numerator / denominator
            m_CDS = m_VPc  # Hypothèse : condensation totale

            st.success(f"🔹Débit vapeur entrante VPc calculé = {m_VPc:.2f} t/h")
            st.success(f"🔹Débit des condensats = {m_CDS:.2f} t/h")
            st.success(f"🔹Débit de l'eau évaporée calculé = {m_Eevap:.2f} t/h")
            st.success(f"🔹Volume de la masse cuite entrante calculé = {V_MCR32:.2f} t/h")

            st.session_state["resultats_machines"]["Cuite R4"] = {
                "Vvkt": m_VPc,
                "CDS": m_CDS,
                "Eau évaporée": m_Eevap,
                "Volume entrant de la masse cuite": V_MCR32
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")


def bilan_cuiteA():
    st.header("Bilan de la cuite A")
    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, volume entrant, débit volumiques")

    h_VPc = st.number_input("Enthalpie de la vapeur compressée (kJ/kg)", min_value=0.0)
    h_CDS = st.number_input("Enthalpie des condensats (kJ/kg)", min_value=0.0)
    h_Eevap = st.number_input("Enthalpie de l'eau évaporée (kJ/kg)", min_value=0.0)

    T_MCR4 = st.number_input("Température de la masse cuite issue de la cuite R4 (°C)", min_value=0.0)
    Brix_MCR4 = st.number_input("Brix de la masse cuite issue de la R4 (%)", min_value=0.0, max_value=100.0)

    V_MCA = st.number_input("Volume de la masse cuite sortante (m³)", min_value=0.0)
    T_MCA = st.number_input("Température de la masse cuite sortante (°C)", min_value=0.0)
    Brix_MCA = st.number_input("Brix de la masse cuite sortante (%)", min_value=0.0, max_value=100.0)


    if st.button("Calculer VPc - Cuite A"):
        try:
            Cp_MCR4 = Cp(Brix_MCR4)
            Cp_MCA = Cp(Brix_MCA)
            D_MCA = D(Brix_MCA)
            D_MCR4 = D(Brix_MCR4)

            # Bilan matière
            V_MCR4 = (D_MCA * V_MCA * (Brix_MCA / 100)) /(D_MCR4 * (Brix_MCR4 / 100))
            m_MCR4 = D_MCR4 * V_MCR4 * (Brix_MCR4 / 100)
            m_MCA = D_MCA * V_MCA * (Brix_MCA / 100)
            m_Eevap = V_MCR4 - V_MCA

            # Bilan énergétique
            numerator = m_Eevap * h_Eevap + V_MCA * Cp_MCA * T_MCA - V_MCR4 * Cp_MCR4 * T_MCR4 
            denominator = h_VPc - h_CDS

            if denominator == 0:
                st.error("Erreur : h_VPc et h_CDS sont égaux → division impossible.")
                return

            m_VPc = numerator / denominator
            m_CDS = m_VPc  # Hypothèse : condensation totale

            st.success(f"🔹Débit vapeur entrante VPc calculé = {m_VPc:.2f} t/h")
            st.success(f"🔹Débit des condensats = {m_CDS:.2f} t/h")
            st.success(f"🔹Débit de l'eau évaporée calculé = {m_Eevap:.2f} t/h")
            st.success(f"🔹Volume de la masse cuite entrante calculé = {V_MCR4:.2f} t/h")

            st.session_state["resultats_machines"]["Cuite A"] = {
                "Vvkt": m_VPc,
                "CDS": m_CDS,
                "Eau évaporée": m_Eevap,
                "Volume entrant de la masse cuite": V_MCR4
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")



def bilan_cuiteB():
    st.header("Bilan de la cuite B")
    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, volume entrant, débit volumiques")

    h_VPc = st.number_input("Enthalpie de la vapeur compressée (kJ/kg)", min_value=0.0)
    h_CDS = st.number_input("Enthalpie des condensats (kJ/kg)", min_value=0.0)
    h_Eevap = st.number_input("Enthalpie de l'eau évaporée (kJ/kg)", min_value=0.0)

    T_MCA = st.number_input("Température de la masse cuite issue de la cuite A (°C)", min_value=0.0)
    Brix_MCA = st.number_input("Brix de la masse cuite issue de la A (%)", min_value=0.0, max_value=100.0)

    V_MCB = st.number_input("Volume de la masse cuite sortante (m³)", min_value=0.0)
    T_MCB = st.number_input("Température de la masse cuite sortante (°C)", min_value=0.0)
    Brix_MCB = st.number_input("Brix de la masse cuite sortante (%)", min_value=0.0, max_value=100.0)


    if st.button("Calculer VPc - Cuite B"):
        try:
            Cp_MCB = Cp(Brix_MCB)
            Cp_MCA = Cp(Brix_MCA)
            D_MCA = D(Brix_MCA)
            D_MCB = D(Brix_MCB)

            # Bilan matière
            V_MCA = (D_MCB * V_MCB * (Brix_MCB / 100)) /(D_MCA * (Brix_MCA / 100))
            m_MCB = D_MCB * V_MCB * (Brix_MCB / 100)
            m_MCA = D_MCA * V_MCA * (Brix_MCA / 100)
            m_Eevap = V_MCA - V_MCB

            # Bilan énergétique
            numerator = m_Eevap * h_Eevap + V_MCB * Cp_MCB * T_MCB - V_MCA * Cp_MCA * T_MCA 
            denominator = h_VPc - h_CDS

            if denominator == 0:
                st.error("Erreur : h_VPc et h_CDS sont égaux → division impossible.")
                return

            m_VPc = numerator / denominator
            m_CDS = m_VPc  # Hypothèse : condensation totale

            st.success(f"🔹Débit vapeur entrante VPc calculé = {m_VPc:.2f} t/h")
            st.success(f"🔹Débit des condensats = {m_CDS:.2f} t/h")
            st.success(f"🔹Débit de l'eau évaporée calculé = {m_Eevap:.2f} t/h")
            st.success(f"🔹Volume de la masse cuite entrante calculé = {V_MCA:.2f} t/h")

            st.session_state["resultats_machines"]["Cuite B"] = {
                "Vvkt": m_VPc,
                "CDS": m_CDS,
                "Eau évaporée": m_Eevap,
                "Volume entrant de la masse cuite": V_MCA
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")


def bilan_cuiteC():
    st.header("Bilan de la cuite C")
    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, volume entrant, débit volumiques")

    h_VPc = st.number_input("Enthalpie de la vapeur compressée (kJ/kg)", min_value=0.0)
    h_CDS = st.number_input("Enthalpie des condensats (kJ/kg)", min_value=0.0)
    h_Eevap = st.number_input("Enthalpie de l'eau évaporée (kJ/kg)", min_value=0.0)

    T_MCB = st.number_input("Température de la masse cuite issue de la cuite B (°C)", min_value=0.0)
    Brix_MCB = st.number_input("Brix de la masse cuite issue de la B (%)", min_value=0.0, max_value=100.0)

    V_MCC = st.number_input("Volume de la masse cuite sortante (m³)", min_value=0.0)
    T_MCC = st.number_input("Température de la masse cuite sortante (°C)", min_value=0.0)
    Brix_MCC = st.number_input("Brix de la masse cuite sortante (%)", min_value=0.0, max_value=100.0)


    if st.button("Calculer VPc - Cuite C"):
        try:
            Cp_MCB = Cp(Brix_MCB)
            Cp_MCC = Cp(Brix_MCC)
            D_MCC = D(Brix_MCC)
            D_MCB = D(Brix_MCB)

            # Bilan matière
            V_MCB = (D_MCC * V_MCC * (Brix_MCC / 100)) /(D_MCB * (Brix_MCB / 100))
            m_MCB = D_MCB * V_MCB * (Brix_MCB / 100)
            m_MCC = D_MCC * V_MCC * (Brix_MCC / 100)
            m_Eevap = V_MCB - V_MCC

            # Bilan énergétique
            numerator = m_Eevap * h_Eevap + V_MCC * Cp_MCC * T_MCC - V_MCB * Cp_MCB * T_MCB 
            denominator = h_VPc - h_CDS

            if denominator == 0:
                st.error("Erreur : h_VPc et h_CDS sont égaux → division impossible.")
                return

            m_VPc = numerator / denominator
            m_CDS = m_VPc  # Hypothèse : condensation totale

            st.success(f"🔹Débit vapeur entrante VPc calculé = {m_VPc:.2f} t/h")
            st.success(f"🔹Débit des condensats = {m_CDS:.2f} t/h")
            st.success(f"🔹Débit de l'eau évaporée calculé = {m_Eevap:.2f} t/h")
            st.success(f"🔹Volume de la masse cuite entrante calculé = {V_MCB:.2f} t/h")

            st.session_state["resultats_machines"]["Cuite C"] = {
                "Vvkt": m_VPc,
                "CDS": m_CDS,
                "Eau évaporée": m_Eevap,
                "Volume entrant de la masse cuite": V_MCB
            }
        
        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")
#################################################################################################################################################################################################################
def bilan_degraissage_cuites():
    st.header("Bilan global du dégraissage – Débit vapeur total (VPT)")

    try:
        # Vérifier si des résultats existent
        if "resultats_machines" not in st.session_state:
            st.warning("⚠️ Aucun résultat trouvé. Lance d’abord les calculs pour chaque cuite.")
            return

        resultats = st.session_state["resultats_machines"]

        # Collecter tous les débits disponibles
        debits_cuites = []
        for nom_cuite, valeurs in resultats.items():
            if isinstance(valeurs, dict) and "Débit vapeur (t/h)" in valeurs:
                debits_cuites.append((nom_cuite, valeurs["Débit vapeur (t/h)"]))

        # Vérifier si on a au moins un résultat
        if not debits_cuites:
            st.warning("⚠️ Aucun débit trouvé. Lance d’abord les calculs pour chaque cuite.")
            return

        # Affichage des détails
        st.subheader("🔹 Débits vapeur par cuite")
        for cuite, debit in debits_cuites:
            st.write(f"- {cuite} : {debit:.3f} t/h")

        # Somme totale
        debit_total = sum(val for _, val in debits_cuites)

        st.success(f"💡 Débit total vapeur nécessaire au dégraissage = {debit_total:.3f} t/h")

        # Sauvegarde du bilan global
        st.session_state["resultats_machines"]["Dégraissage des cuites STG1+STG2"] = {
            "Débit total (t/h)": debit_total
        }
    except Exception as e:
        st.error(f"Erreur dans le calcul du bilan global : {e}")
###
def bilan_degraissage_cuite710HL():
    st.header("Calcul du débit vapeur VPT suffisant au dégraissage de la cuite 710HL ")
    # Paramètres à saisir
    V_occ = st.number_input("Volume occupé par la masse cuite à dégraisser (m³)", min_value=0.0)
    h_VPT = st.number_input("Enthalpie de la vapeur VPT (kJ/kg)", min_value=0.0)
    T_VPT = st.number_input("Température de la masse cuite chauffée  (°C)", min_value=0.0)
    T_MC = st.number_input("Température initiale de la masse cuite à dégraisser (°C)", min_value=0.0)
    Brix_MC = st.number_input("Brix de la masse cuite à dégraisser (%)", max_value=100.0)
    if st.button("Calculer débit vapeur VPT"):
        try:

            delta_T= T_VPT-T_MC
            rho=D(Brix_MC)
            Cp_MC=Cp(Brix_MC)
            Q = Cp_MC * rho * V_occ * delta_T 
            if h_VPT == 0:
                st.error("Erreur : h_VPT ne peut pas être nul → division impossible.")
                return

            m_VPT_710 = Q / h_VPT  # (kg)
        
            # Résultats
            st.success(f"🔹 Débit vapeur VPT = {m_VPT_710:.2f} t/h")

            # Sauvegarde dans la session
            st.session_state["resultats_machines"]["Dégraissage de la cuite 710HL"] = {
                "Débit vapeur (t/h)": m_VPT_710,
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")

####
def bilan_degraissage_cuite550HL():
    st.header("Calcul du débit vapeur VPT suffisant au dégraissage de la cuite 550HL ")
    # Paramètres à saisir
    V_occ = st.number_input("Volume occupé par la masse cuite à dégraisser (m³)", min_value=0.0)
    h_VPT = st.number_input("Enthalpie de la vapeur VPT (kJ/kg)", min_value=0.0)
    T_VPT = st.number_input("Température de la masse cuite chauffée  (°C)", min_value=0.0)
    T_MC = st.number_input("Température initiale de la masse cuite à dégraisser (°C)", min_value=0.0)
    Brix_MC = st.number_input("Brix de la masse cuite à dégraisser (%)", max_value=100.0)
    if st.button("Calculer débit vapeur VPT"):
        try:

            delta_T= T_VPT-T_MC
            rho=D(Brix_MC)
            Cp_MC=Cp(Brix_MC)
            Q = Cp_MC * rho * V_occ * delta_T 
            if h_VPT == 0:
                st.error("Erreur : h_VPT ne peut pas être nul → division impossible.")
                return

            m_VPT_550 = Q / h_VPT  # (kg)
        
            # Résultats
            st.success(f"🔹 Débit vapeur VPT = {m_VPT_550:.2f} t/h")

            # Sauvegarde dans la session
            st.session_state["resultats_machines"]["Dégraissage de la cuite 550HL"] = {
                "Débit vapeur (t/h)": m_VPT_550,
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")

###
def bilan_degraissage_cuiteR2():
    st.header("Calcul du débit vapeur VPT suffisant au dégraissage de la cuite R2 ")
    # Paramètres à saisir
    V_occ = st.number_input("Volume occupé par la masse cuite à dégraisser (m³)", min_value=0.0)
    h_VPT = st.number_input("Enthalpie de la vapeur VPT (kJ/kg)", min_value=0.0)
    T_VPT = st.number_input("Température de la masse cuite chauffée  (°C)", min_value=0.0)
    T_MC = st.number_input("Température initiale de la masse cuite à dégraisser (°C)", min_value=0.0)
    Brix_MC = st.number_input("Brix de la masse cuite à dégraisser (%)", max_value=100.0)
    if st.button("Calculer débit vapeur VPT"):
        try:

            delta_T= T_VPT-T_MC
            rho=D(Brix_MC)
            Cp_MC=Cp(Brix_MC)
            Q = Cp_MC * rho * V_occ * delta_T 
            if h_VPT == 0:
                st.error("Erreur : h_VPT ne peut pas être nul → division impossible.")
                return

            m_VPT_R2 = Q / h_VPT  # (kg)
        
            # Résultats
            st.success(f"🔹 Débit vapeur VPT = {m_VPT_R2:.2f} t/h")

            # Sauvegarde dans la session
            st.session_state["resultats_machines"]["Dégraissage de la cuite R2"] = {
                "Débit vapeur (t/h)": m_VPT_R2,
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")
###
def bilan_degraissage_cuiteA():
    st.header("Calcul du débit vapeur VPT suffisant au dégraissage de la cuite A ")
    # Paramètres à saisir
    V_occ = st.number_input("Volume occupé par la masse cuite à dégraisser (m³)", min_value=0.0)
    h_VPT = st.number_input("Enthalpie de la vapeur VPT (kJ/kg)", min_value=0.0)
    T_VPT = st.number_input("Température de la masse cuite chauffée  (°C)", min_value=0.0)
    T_MC = st.number_input("Température initiale de la masse cuite à dégraisser (°C)", min_value=0.0)
    Brix_MC = st.number_input("Brix de la masse cuite à dégraisser (%)", max_value=100.0)
    if st.button("Calculer débit vapeur VPT"):
        try:

            delta_T= T_VPT-T_MC
            rho=D(Brix_MC)
            Cp_MC=Cp(Brix_MC)
            Q = Cp_MC * rho * V_occ * delta_T 
            if h_VPT == 0:
                st.error("Erreur : h_VPT ne peut pas être nul → division impossible.")
                return

            m_VPT_A = Q / h_VPT  # (kg)
        
            # Résultats
            st.success(f"🔹 Débit vapeur VPT = {m_VPT_A:.2f} t/h")

            # Sauvegarde dans la session
            st.session_state["resultats_machines"]["Dégraissage de la cuite A"] = {
                "Débit vapeur (t/h)": m_VPT_A,
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")

###
def bilan_degraissage_cuiteB():
    st.header("Calcul du débit vapeur VPT suffisant au dégraissage de la cuite B ")
    # Paramètres à saisir
    V_occ = st.number_input("Volume occupé par la masse cuite à dégraisser (m³)", min_value=0.0)
    h_VPT = st.number_input("Enthalpie de la vapeur VPT (kJ/kg)", min_value=0.0)
    T_VPT = st.number_input("Température de la masse cuite chauffée  (°C)", min_value=0.0)
    T_MC = st.number_input("Température initiale de la masse cuite à dégraisser (°C)", min_value=0.0)
    Brix_MC = st.number_input("Brix de la masse cuite à dégraisser (%)", max_value=100.0)
    if st.button("Calculer débit vapeur VPT"):
        try:

            delta_T= T_VPT-T_MC
            rho=D(Brix_MC)
            Cp_MC=Cp(Brix_MC)
            Q = Cp_MC * rho * V_occ * delta_T 
            if h_VPT == 0:
                st.error("Erreur : h_VPT ne peut pas être nul → division impossible.")
                return

            m_VPT_B = Q / h_VPT  # (kg)
        
            # Résultats
            st.success(f"🔹 Débit vapeur VPT = {m_VPT_B:.2f} t/h")

            # Sauvegarde dans la session
            st.session_state["resultats_machines"]["Dégraissage de la cuite B"] = {
                "Débit vapeur (t/h)": m_VPT_B,
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")
###
def bilan_degraissage_cuiteC():
    st.header("Calcul du débit vapeur VPT suffisant au dégraissage de la cuite C ")
    # Paramètres à saisir
    V_occ = st.number_input("Volume occupé par la masse cuite à dégraisser (m³)", min_value=0.0)
    h_VPT = st.number_input("Enthalpie de la vapeur VPT (kJ/kg)", min_value=0.0)
    T_VPT = st.number_input("Température de la masse cuite chauffée  (°C)", min_value=0.0)
    T_MC = st.number_input("Température initiale de la masse cuite à dégraisser (°C)", min_value=0.0)
    Brix_MC = st.number_input("Brix de la masse cuite à dégraisser (%)", max_value=100.0)
    if st.button("Calculer débit vapeur VPT"):
        try:

            delta_T= T_VPT-T_MC
            rho=D(Brix_MC)
            Cp_MC=Cp(Brix_MC)
            Q = Cp_MC * rho * V_occ * delta_T 
            if h_VPT == 0:
                st.error("Erreur : h_VPT ne peut pas être nul → division impossible.")
                return

            m_VPT_C = Q / h_VPT  # (kg)
        
            # Résultats
            st.success(f"🔹 Débit vapeur VPT = {m_VPT_C:.2f} t/h")

            # Sauvegarde dans la session
            st.session_state["resultats_machines"]["Dégraissage de la cuite C"] = {
                "Débit vapeur (t/h)": m_VPT_C,
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")

###
def bilan_degraissage_cuiteR31_R32_R33():
    st.header("Calcul du débit vapeur VPT suffisant au dégraissage des cuites R31-R32-R33 ")
    # Paramètres à saisir
    V_occ = st.number_input("Volume occupé par la masse cuite à dégraisser (m³)", min_value=0.0)
    h_VPT = st.number_input("Enthalpie de la vapeur VPT (kJ/kg)", min_value=0.0)
    T_VPT = st.number_input("Température de la masse cuite chauffée  (°C)", min_value=0.0)
    T_MC = st.number_input("Température initiale de la masse cuite à dégraisser (°C)", min_value=0.0)
    Brix_MC = st.number_input("Brix de la masse cuite à dégraisser (%)", max_value=100.0)
    if st.button("Calculer débit vapeur VPT"):
        try:

            delta_T= T_VPT-T_MC
            rho=D(Brix_MC)
            Cp_MC=Cp(Brix_MC)
            Q = Cp_MC * rho * V_occ * delta_T 
            if h_VPT == 0:
                st.error("Erreur : h_VPT ne peut pas être nul → division impossible.")
                return

            m_VPT_R31= Q / h_VPT  # (kg)
            m_VPT_3x=m_VPT_R31*3

        
            # Résultats
            st.success(f"🔹 Débit vapeur VPT = {m_VPT_3x:.2f} t/h")

            # Sauvegarde dans la session
            st.session_state["resultats_machines"]["Dégraissage des cuites R31, R32 & R33"] = {
               "Débit vapeur (t/h) d'une seule cuite" :m_VPT_R31,
                "Débit vapeur (t/h)": m_VPT_3x
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")
#####################################################################################################################################################################################
def bilan_gazsIncondensables():
    st.header("🌍 Bilan global des gazs incondensables ")

    try:
        resultats = st.session_state.get("resultats_machines", {})

        debit_R2_710 = resultats.get("Échappement de la VPT & Gazs incondensables des cuites 710HL & R2", {}).get("Débit total (t/h)", 0.0)
        debit_550HL = resultats.get("Échappement de la VPT & Gazs incondensables de la cuite 550HL", {}).get("Débit total (t/h)", 0.0)

        # On multiplie le débit R2+710HL par 2 comme demandé
        debit_R2_710_corrige = debit_R2_710 * 2

        debit_total = debit_R2_710_corrige + debit_550HL

        if debit_total == 0:
            st.warning("⚠️ Aucun débit calculé pour les gazs incondensables (710HL/R2 ou 550HL).")
            return

        # Résultats
        st.success(f"🔹 Débit corrigé (710HL + R2, multiplié par 2) = {debit_R2_710_corrige:.3f} t/h")
        st.success(f"🔹 Débit cuite 550HL = {debit_550HL:.3f} t/h")
        st.success(f"🌍 Débit total = {debit_total:.3f} t/h")

        # Sauvegarde dans la session
        st.session_state["resultats_machines"]["Échappement de la VPT & Gazs incondensables"] = {
            "Débit corrigé (710HL+R2) (t/h)": debit_R2_710_corrige,
            "Débit cuite 550HL (t/h)": debit_550HL,
            "Débit total (t/h)": debit_total,
        }

    except Exception as e:
        st.error(f"Erreur dans le calcul du bilan global : {e}")


def bilan_gazsIncondensables_cuiteR2_710HL():
    st.header("Calcul d’écoulement compressible (VPT+Gazs incondensables)")
    st.info("Calcul du flux massique G et le débit total en fonction de la pression, de la température et des dimensions des conduites.")
    # Entrées principales
    P1_bar = st.number_input("Pression de la VPT (bar)", min_value=0.0, value=1.2)
    P2_bar = st.number_input("Pression des gazs incondensables (bar)", min_value=0.0, value=0.25)
    T_C = st.number_input("Température des gazs incondensables (°C)", min_value=-100.0, value=65.0)
    gamma = st.number_input("Coefficient adiabatique γ de l'air", min_value=1.0, value=1.4)
    M = st.number_input("Masse molaire des gazs incondensables M (g/mol)", min_value=0.0, value=28.965)
    
    # Géométrie des conduites
    n_conduites = st.number_input("Nombre de conduites", min_value=1, value=8)
    d_mm = st.number_input("Diamètre intérieur d’une conduite (mm)", min_value=1.0, value=20.0)

    if st.button("Calculer l’écoulement compressible"):
        try:
            # Conversion unités
            R=8.314/(M*0.001)
            P1 = P1_bar * 1e5  # Pa
            P2 = P2_bar * 1e5  # Pa
            T_K = T_C + 273.15  # K
            r_m = (d_mm / 1000) / 2  # rayon en m

            # Nombre de Mach à partir du rapport de pressions (écoulement isentropique)
            M = math.sqrt(((P2/P1)**(-(gamma-1)/gamma) - 1) * (2/(gamma-1)))

            # Flux massique G
            G = (P2 * M * math.sqrt(gamma)) / math.sqrt(R * T_K)  # kg/m².s

            # Débit massique par conduite
            A = math.pi * r_m**2
            m_dot_1 = G * A  # kg/s
            m_dot_total = m_dot_1 * n_conduites  # kg/s
            m_dot_total_th = m_dot_total * 3600 / 1000  # t/h

            # Résultats
            st.success(f"🔹 Nombre de Mach M = {M:.4f}")
            st.success(f"🔹 Flux massique G = {G:.3f} kg/(m²·s)")
            st.success(f"🔹 Débit par conduite = {m_dot_1:.5f} kg/s")
            st.success(f"🔹 Débit total ({n_conduites} conduites) = {m_dot_total:.5f} kg/s = {m_dot_total_th:.3f} t/h")

            # Sauvegarde dans la session
            st.session_state["resultats_machines"]["Échappement de la VPT & Gazs incondensables des cuites 710HL & R2"] = {
                "Mach": M,
                "Flux massique G (kg/m².s)": G,
                "Débit 1 conduite (kg/s)": m_dot_1,
                "Débit total (kg/s)": m_dot_total,
                "Débit total (t/h)": m_dot_total_th,
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")

###

def bilan_gazsIncondensables_cuite550HL():
    st.header("Calcul d’écoulement compressible (VPT+Gazs incondensables)")
    st.info("Calcul du flux massique G et le débit total en fonction de la pression, de la température et des dimensions des conduites.")
    # Entrées principales
    P1_bar = st.number_input("Pression de la VPT (bar)", min_value=0.0, value=1.2)
    P2_bar = st.number_input("Pression des gazs incondensables (bar)", min_value=0.0, value=0.25)
    T_C = st.number_input("Température des gazs incondensables (°C)", min_value=-100.0, value=65.0)
    gamma = st.number_input("Coefficient adiabatique γ de l'air", min_value=1.0, value=1.4)
    M = st.number_input("Masse molaire des gazs incondensables M (g/mol)", min_value=0.0, value=28.965)
    
    # Géométrie des conduites
    n_conduites = st.number_input("Nombre de conduites", min_value=1, value=3)
    d_mm = st.number_input("Diamètre intérieur d’une conduite (mm)", min_value=1.0, value=30.0)

    if st.button("Calculer l’écoulement compressible"):
        try:
            # Conversion unités
            R=8.314/(M*0.001)
            P1 = P1_bar * 1e5  # Pa
            P2 = P2_bar * 1e5  # Pa
            T_K = T_C + 273.15  # K
            r_m = (d_mm / 1000) / 2  # rayon en m

            # Nombre de Mach à partir du rapport de pressions (écoulement isentropique)
            M = math.sqrt(((P2/P1)**(-(gamma-1)/gamma) - 1) * (2/(gamma-1)))

            # Flux massique G
            G = (P2 * M * math.sqrt(gamma)) / math.sqrt(R * T_K)  # kg/m².s

            # Débit massique par conduite
            A = math.pi * r_m**2
            m_dot_1 = G * A  # kg/s
            m_dot_total = m_dot_1 * n_conduites  # kg/s
            m_dot_total_th = m_dot_total * 3600 / 1000  # t/h

            # Résultats
            st.success(f"🔹 Nombre de Mach M = {M:.4f}")
            st.success(f"🔹 Flux massique G = {G:.3f} kg/(m²·s)")
            st.success(f"🔹 Débit par conduite = {m_dot_1:.5f} kg/s")
            st.success(f"🔹 Débit total ({n_conduites} conduites) = {m_dot_total:.5f} kg/s = {m_dot_total_th:.3f} t/h")

            # Sauvegarde dans la session
            st.session_state["resultats_machines"]["Échappement de la VPT & Gazs incondensables de la cuite 550HL"] = {
                "Mach": M,
                "Flux massique G (kg/m².s)": G,
                "Débit 1 conduite (kg/s)": m_dot_1,
                "Débit total (kg/s)": m_dot_total,
                "Débit total (t/h)": m_dot_total_th,
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")
##################################################################################################### 
def bilan_soufflage_filtre():
    st.header("Calcul du débit de la VPT pour les filtres DIASTAR")
    st.info("Ce module estime la consommation de vapeur des filtres DIASTAR en fonction des capacités, du nombre de filtres et de la densité de la vapeur.")

    # Paramètres des filtres
    N1 = st.number_input("Nombre de filtres de capacité C1 (m³/cycle)", min_value=0, value=6)
    C1 = st.number_input("Capacité d’un filtre type 1 (m³/cycle)", min_value=0.0, value=40.0)
    N2 = st.number_input("Nombre de filtres de capacité C2 (m³/cycle)", min_value=0, value=6)
    C2 = st.number_input("Capacité d’un filtre type 2 (m³/cycle)", min_value=0.0, value=30.0)

    # Données de fonctionnement
    t_cycle = st.number_input("Durée d’un cycle (h/jour)", min_value=0.0, value=2.0)
    rho = st.number_input("Densité de la vapeur (kg/m³)", min_value=0.0, value=1.46)

    if st.button("Calculer débit vapeur VPT - DIASTAR"):
        try:
            # Volume total de vapeur consommé par jour (m³/jour)
            V_total = (N1 * C1 + N2 * C2) * t_cycle  

            # Débit volumique journalier
            Q_day = V_total  # m³/jour

            # Débit volumique horaire
            Q_hour = Q_day / 24  # m³/h

            # Débit massique en t/h (selon formule donnée)
            m_VPT = (V_total * rho) / (24 * 1000)  # t/h

            # Résultats
            st.success(f"🔹 Volume total vapeur par jour = {V_total:.2f} m³/jour")
            st.success(f"🔹 Débit volumique horaire = {Q_hour:.2f} m³/h")
            st.success(f"🔹 Débit total = {m_VPT:.4f} t/h")

            # Sauvegarde session
            st.session_state["resultats_machines"]["Soufflage des filtres"] = {
                "Volume total (m³/jour)": V_total,
                "Débit volumique (m³/h)": Q_hour,
                "Débit total (t/h)": m_VPT,
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")
########################################################################################################
def bilan_ECH_commune_carbonatée():
    st.header("Bilan de l'échangeur de la commune carbonatée")
    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, débit volumiques")

    h_VPT = st.number_input("Enthalpie vapeur VPT (kJ/kg)", min_value=0.0)

    m_FC = st.number_input("Débit de l'entrée (t/h)", min_value=0.0)
    T_FC = st.number_input("Température de l'entrée (°C)", min_value=0.0)
    Brix_FC = st.number_input("Brix de l'entrée  (%)", min_value=0.0, max_value=100.0, value=100.0)

    m_CC = st.number_input("Débit de la sortie  (t/h)", min_value=0.0)
    T_CC = st.number_input("Température de la sortie  (°C)", min_value=0.0)
    Brix_CC = st.number_input("Brix de la sortie (%)", min_value=0.0, max_value=100.0, value=100.0)

    h_CDS = st.number_input("Enthalpie des condensats (kJ/kg)", min_value=0.0)


    if st.button("Calculer VPT - ECH Commune Carbonatée"):
        try:
            Cp_CC = Cp(Brix_CC)
            Cp_FC = Cp(Brix_FC)

            numerator = m_CC * Cp_CC* T_CC - m_FC * Cp_FC * T_FC
            denominator = h_VPT - h_CDS

            if denominator == 0:
                st.error("Erreur : enthalpie vapeur VPT = 0 → division impossible.")
                return

            m_VPT = numerator / denominator
            m_CDS = m_VPT

            st.success(f"🔹Débit vapeur entrante VPT calculé = {m_VPT:.2f} t/h")

            # Enregistrement dans session_state
            st.session_state["resultats_machines"]["ECH Commune Carbonatée"] = {
                "VPT": m_VPT,
                "CDS": m_CDS
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")
######################################################################################## 


def afficher_machine(machine, vapeur):
    # Section par machine
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### {machine}")
    with col2:
        # Checkbox pour activer/désactiver la machine
        etat_cle = f"{machine}_active"
        st.session_state.setdefault(etat_cle, True)
        st.checkbox("Activer", value=st.session_state[etat_cle], key=etat_cle)

    # Si la machine est active, afficher les champs de saisie
    if st.session_state[etat_cle]:
        debit = st.number_input(f"Débit {vapeur} (kg/h)", min_value=0.0, key=f"{machine}_debit")
        temperature = st.number_input(f"Température (°C)", min_value=0.0, key=f"{machine}_temp")
        # Enregistre les données si besoin
        st.session_state["resultats_machines"][machine] = {
            f"{vapeur}_debit": debit,
            f"{vapeur}_temp": temperature
        }
    else:
        # Si désactivée, supprimer ses résultats du dictionnaire
        st.session_state["resultats_machines"].pop(machine, None)


# Mapping
bilan_machines = {
    "CEFT 2400": bilan_ceft_2400,
    "CEFT 1300": bilan_ceft_1300,
    "Bouilleur": bilan_bouilleur,
    "ECH Bouilleur": bilan_echangeur_bouilleur,

    "CEFT 1600": bilan_ceft_1600,
    "VKT": bilan_vkt,
    "ECH 2400 (VP1)" : bilan_echangeur_2400_VP1,

    "DCH Fondoir F0" : bilan_dch_f0,
    "DCH Fondoir F1" : bilan_dch_f1,
    "DCH ES": bilan_dch_ES,
    "ECH EA" : bilan_echangeur_EA,
    "ECH ED" : bilan_echangeur_ED,
    "Condenseur": bilan_condenseur,
    
    "DCH Fondoir F2" : bilan_dch_f2,
    "Cuite 710HL" : bilan_cuite710,
    "Cuite 550HL" : bilan_cuite550,
    "Cuite R2" : bilan_cuiteR2,
    "ECH sécheur" : bilan_ECH_sécheur,
    "ECH 2400 (VPT)" : bilan_echangeur_2400_VPT,

    "Cuite R31" : bilan_cuiteR31,
    "Cuite R32" : bilan_cuiteR32,
    "Cuite R4" : bilan_cuiteR4,
    "Cuite A" : bilan_cuiteA,
    "Cuite B" : bilan_cuiteB,
    "Cuite C" : bilan_cuiteC,

    "Dégraissage des cuites STG1+STG2" : bilan_degraissage_cuites,
    "Dégraissage de la cuite 710HL": bilan_degraissage_cuite710HL,
    "Dégraissage de la cuite 550HL" : bilan_degraissage_cuite550HL,
    "Dégraissage de la cuite R2" : bilan_degraissage_cuiteR2,
    "Dégraissage de la cuite A" : bilan_degraissage_cuiteA,
    "Dégraissage de la cuite B" :bilan_degraissage_cuiteB,
    "Dégraissage de la cuite C" : bilan_degraissage_cuiteC,
    "Dégraissage des cuites R31, R32 & R33" : bilan_degraissage_cuiteR31_R32_R33,

    "Échappement de la VPT & Gazs incondensables" :bilan_gazsIncondensables,
    "Échappement de la VPT & Gazs incondensables des cuites 710HL & R2" :bilan_gazsIncondensables_cuiteR2_710HL,
    "Échappement de la VPT & Gazs incondensables de la cuite 550HL" : bilan_gazsIncondensables_cuite550HL,
    "Soufflage des filtres" : bilan_soufflage_filtre,
    "ECH Commune Carbonatée" :bilan_ECH_commune_carbonatée


}

# Sélection de la machine
selected_machine = st.selectbox("🔧 Choisissez une machine :", machines)

if selected_machine:
    if selected_machine in bilan_machines:
        bilan_machines[selected_machine]()
    else:
        st.info("Pas encore de bilan défini pour cette machine.")


# ---- Résultats cumulés ----
st.markdown("---")
st.subheader("📊 Résultats enregistrés")



if st.session_state["resultats_machines"]:
    for machine, resultats in st.session_state["resultats_machines"].items():
        st.markdown(f"### 🔧 {machine}")
        data = {k: [f"{v:.2f} t/h"] for k, v in resultats.items()}
        st.table(data)
    
else:
    st.info("Aucun résultat disponible pour le moment.")











def regroupement_par_vapeur(resultats):
    # Dictionnaire machine → vapeur entrante principale
    machine_to_vapeur = { 
        "CEFT 2400": "VE",
        "CEFT 1300": "VE",
        "Bouilleur": "VE",
        "ECH Bouilleur": "VE",

        "CEFT 1600": "VP1",
        "VKT": "VP1",
        "ECH 2400 (VP1)": "VP1",
        
        "DCH Fondoir F0": "VP2",
        "DCH Fondoir F1": "VP2",
        "DCH ES": "VP2",
        "ECH EA": "VP2",
        "ECH ED": "VP2",
        "Condenseur": "VP2",

        "DCH Fondoir F2": "VPT",
        "Cuite 710HL": "VPT",
        "Cuite 550HL": "VPT",
        "Cuite R2": "VPT",
        "ECH 2400 (VPT)": "VPT",
        "ECH sécheur" : "VPT",
        "Dégraissage des cuites STG1+STG2" : "VPT",
        "Échappement de la VPT & Gazs incondensables" :"VPT",
        "Soufflage des filtres" : "VPT",
        "ECH Commune Carbonatée" :"VPT",
    

        "Cuite R31": "Vvkt",
        "Cuite R32": "Vvkt",
        "Cuite R4": "Vvkt",
        "Cuite A": "Vvkt",
        "Cuite B": "Vvkt",
        "Cuite C": "Vvkt"
    }

    # Initialisation
    regroupes = {
        "VE": {},
        "VP1": {},
        "VP2": {},
        "VPT": {},
        "Vvkt": {},
    }

    # Parcours des résultats
    for machine, valeurs in resultats.items():
        vapeur = machine_to_vapeur.get(machine)
        if vapeur:
            regroupes[vapeur][machine] = valeurs

    return regroupes

    # Supprimer les groupes vides

groupes = regroupement_par_vapeur(st.session_state["resultats_machines"])


from fpdf import FPDF
import matplotlib.pyplot as plt
import streamlit as st
import io
import os

class CustomPDF(FPDF):
    def footer(self):
        self.set_y(-10)
        self.set_font("Times", 'B', 12)
        self.cell(0, 10, "Réalisée par : ABDALI Jihane", align='R')

import matplotlib.pyplot as plt
import numpy as np
import io

def creer_pie_chart(labels, sizes, title):
    fig, ax = plt.subplots(figsize=(7, 6))  # Légèrement plus large

    def autopct_fmt(pct):
        return f'{pct:.1f}%' if pct > 1 else ''

    wedges, texts, autotexts = ax.pie(
        sizes,
        autopct=autopct_fmt,
        startangle=90,
        textprops=dict(color="black"),
    )

    ax.axis('equal')
    plt.title(title)

    # 🔹 Ajouter légende à droite comme une key
    total = sum(sizes)
    legend_labels = [
        f"{label} ({s:.0f} t/h)" for label, s in zip(labels, sizes)
    ]
    ax.legend(
        wedges,
        legend_labels,
        title="Machines",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
    )

    # Export image
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf



def ajouter_image_au_pdf(pdf, image_buffer, x=10, y=None, img_width=90):
    image_buffer.seek(0)
    temp_image_path = "temp_chart.png"
    with open(temp_image_path, "wb") as f:
        f.write(image_buffer.read())

    if y is None:
        y = pdf.get_y()
    pdf.image(temp_image_path, x=x, y=y, w=img_width)
    os.remove(temp_image_path)

import tempfile


def inserer_image_apres_texte(pdf, image_buf, largeur_image=120, hauteur_image=90, marge_bas=15, marge_entre_elements=5):
    """
    Insère une image (pie chart) juste après le texte affiché,
    en gérant le saut de page si l'espace restant est insuffisant,
    puis place le curseur juste après l'image avec un petit espace.
    """
    espace_restant = pdf.h - pdf.get_y() - marge_bas

    if espace_restant < hauteur_image:
        pdf.add_page()

    position_y_avant = pdf.get_y()

    with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as tmp_file:
        tmp_file.write(image_buf.getvalue())
        tmp_file.flush()
        pdf.image(tmp_file.name, x=pdf.l_margin, y=position_y_avant, w=largeur_image)

    # Avancer le curseur juste après l'image, avec petite marge
    pdf.set_y(position_y_avant + hauteur_image + marge_entre_elements)



def generer_pdf_resultats():
    pdf = CustomPDF()
    pdf.add_page()
    pdf.set_font("Times", size=12)

    # Logos
    logo1_path = "logo.jpg"
    logo2_path = "logo cosumar.png"
    logo_width = 40
    page_width = pdf.w
    margin = 10

    if os.path.exists(logo1_path):
        pdf.image(logo1_path, x=10, y=8, w=90)
    if os.path.exists(logo2_path):
        pdf.image(logo2_path, x=page_width - margin - logo_width, y=8, w=logo_width)

    pdf.ln(45)
    pdf.set_font("Times", "B", 16)
    pdf.cell(0, 10, "Bilan du circuit de vapeur de la raffinerie COSUMAR", ln=True, align="C")
    pdf.ln(15)

    # Regrouper les machines par vapeur
    groupes = regroupement_par_vapeur(st.session_state["resultats_machines"])

    for vapeur, machines in groupes.items():
        pdf.set_font("Times", "B", 14)
        pdf.cell(0, 10, f"Vapeur {vapeur}", ln=True)
        pdf.set_font("Times", "", 12)

        labels = []
        values = []
        machines_affichees = set()  # Pour éviter doublons dans la même vapeur

        for machine, resultats in machines.items():
            if machine in machines_affichees:
                continue
            machines_affichees.add(machine)

            # Afficher tous les débits de la machine
            pdf.multi_cell(0, 8, f"{machine}")
            for nom_debit, valeur in resultats.items():
                pdf.cell(0, 8, f"{nom_debit} = {valeur:.2f} t/h", ln=True)
            pdf.ln(2)

            # Récupérer la valeur pour cette vapeur pour le pie chart
            # Chercher la valeur la plus représentative pour le pie chart
            valeur_machine_pour_vapeur = None

            # On teste plusieurs clés connues en priorité
            for cle in ["Débit total (t/h)", "Débit global (t/h)", "Débit (t/h)"]:
                if cle in resultats and isinstance(resultats[cle], (int, float)):
                    valeur_machine_pour_vapeur = resultats[cle]
                    break

            # Si aucune clé prioritaire trouvée, on prend la 1ère valeur numérique disponible
            if valeur_machine_pour_vapeur is None:
                for cle, val in resultats.items():
                    if isinstance(val, (int, float)):
                        valeur_machine_pour_vapeur = val
                        break

            # Ajouter au graphique si on a trouvé une valeur
            if valeur_machine_pour_vapeur and valeur_machine_pour_vapeur > 0:
                labels.append(machine)
                values.append(valeur_machine_pour_vapeur)


        if labels and values:
            pdf.ln(5)
            pie_buf = creer_pie_chart(labels, values, f"Répartition de la consommation vapeur {vapeur}")
            inserer_image_apres_texte(pdf, pie_buf)
        

    # Sauvegarde finale
    pdf_output = io.BytesIO()
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    pdf_output.write(pdf_bytes)
    pdf_output.seek(0)
    return pdf_output




try:
    if st.session_state.get("resultats_machines"):
        pdf_buffer = generer_pdf_resultats()
        st.download_button(
            label="📄 Télécharger le bilan en PDF",
            data=pdf_buffer,
            file_name="Bilan_du_circuit_des_vapeurs_de_la_raffinerie.pdf",
            mime="application/pdf"
        )
    else:
        st.info("Aucun résultat à télécharger.")
except Exception as e:
    st.error("Erreur dans la génération du PDF.")
    st.exception(e)
