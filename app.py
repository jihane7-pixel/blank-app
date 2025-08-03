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
    "CEFT 1600", "ECH 2400", "ECH EA", "ECH ED",
    "DCH Fondoir F0", "DCH Fondoir F1", "DCH Fondoir F2", "DCH des eaux sucrées ES", "Condenseur",
    "VKT", "CMV","Station de carbonatation","Cuite 710HL", "Cuite 550HL", "R2", "ECH sécheur", "R31", "R32", "R4", "A", "B", "C","Divers machines restantes"
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
    
    Q_SNC = st.number_input("Débit volumique SNC (m³/h)", min_value=0.0)
    T_SNC = st.number_input("Température SNC (°C)", min_value=0.0)
    Brix_SNC = st.number_input("Brix SNC (%)", min_value=0.0, max_value=100.0)
    
    T_SC1 = st.number_input("Température SC1 (°C)", min_value=0.0)
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
      
    T_SC2 = st.number_input("Température du sirop sortant SC2 (°C)", min_value=0.0)
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
    Q_E = st.number_input("Débit d'eau d'alimentation (m³/h)", min_value=0.0)
    T_E = st.number_input("Température de l'eau d'alimentation (kJ/kg)", min_value=0.0)
    h_VPT = st.number_input("Enthalpie VPT (kJ/kg)", min_value=0.0)
    h_P = st.number_input("Enthalpie purge (kJ/kg)", min_value=0.0)
    Q_CDS = st.number_input("Débit des condesats (m³/h)", min_value=0.0)
    h_CDS = st.number_input("Enthalpie CDS (kJ/kg)", min_value=0.0)

    

    if st.button("Calculer VE - Bouilleur"):
        try:
            Brix_E= Brix_CDS =100
            Cp=4.19
            h_E=Cp*T_E
            m_E=Q_E * D(Brix_E)
            m_CDS=Q_CDS * D(Brix_CDS)
            m_P = 0.02 * m_E
            m_VPT = m_E - m_P
            numerator = m_VPT * h_VPT + m_P * h_P + m_CDS * h_CDS- m_E * h_E
            denominator = h_VE
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
            m_fs=Q_fs * D(Brix_fs)
            m_fe=Q_fe * D(Brix_fe)
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
            m_SCf=Q_SCf * D(Brix_SCf)

            # Récupérer ṁ_VP1' et ṁ_VP1'' des autres bilans
            try:
                m_VP1p = st.session_state["resultats_machines"]["CEFT 2400"]["VP1'"]
                m_VP1pp = st.session_state["resultats_machines"]["CEFT 1300"]["VP1''"]
                
            except KeyError:
                st.warning("⚠️ Impossible de récupérer ṁ_VP1' ou ṁ_VP1'' — calcule d'abord les bilans CEFT 2400 et CEFT 1300.")
                return

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
            st.success(f"🔹Débit du sirop sortant SCf = {Q_SCf:.2f} m³/h = {m_SCf:.2f} t/h" )
            st.success(f"🔹Débit des condensats= {m_VP1:.2f} t/h")

            # Enregistrement
            st.session_state["resultats_machines"]["CEFT 1600"] = {
                "VP1": m_VP1,
                "VP2": m_VP2,
                "CDS": m_VP1,    
            }        

            # Appel immédiat à la comparaison après le calcul
            
            comparer_vp1()


        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")

def comparer_vp1():
    st.subheader("📐 Comparaison entre VP1 calculé et la somme VP1'+VP1''")

    try:
        VP1_calcule = st.session_state["resultats_machines"]["CEFT 1600"]["VP1"]
        VP1_p = st.session_state["resultats_machines"]["CEFT 2400"]["VP1'"]
        VP1_pp = st.session_state["resultats_machines"]["CEFT 1300"]["VP1''"]

        VP1_ref = VP1_p + VP1_pp
        ecart = abs(VP1_calcule - VP1_ref)


        st.write(f"🔹 VP1 calculé = {VP1_calcule:.2f} t/h")
        st.write(f"🔹 VP1' + VP1'' = {VP1_ref:.2f} t/h")
        st.write(f"📏 Écart = {ecart:.2f} t/h")


    except KeyError:
        st.error("❌ Impossible de faire la comparaison — certaines valeurs manquent.")

def bilan_echangeur_EA():
    st.header("Bilan de l'échangeur d'eaux adoucies ")

    st.info("Saisissez les données des entrées et sorties de votre machine : Enthalpies, Températures, coefficient d'échange et surface d'échange.")

    # Saisie des paramètres
    H = st.number_input("Coefficient d'échange thermique H (W/m²·K)", min_value=0.0)
    S = st.number_input("Surface d'échange S (m²)", min_value=0.0)

    T_ee = st.number_input("Température de l'eau entrant (°C)", min_value=0.0)
    T_ea = st.number_input("Température de l'eau adoucie sortante (°C) ", min_value=0.0)

    T_VP1 = st.number_input("Température de la vapeur VP1  (°C)", min_value=0.0)

    h_VP1 = st.number_input("Enthalpie vapeur VP1  (kJ/kg)", min_value=0.0)
    h_CDS = st.number_input("Enthalpie des condensats (kJ/kg)", min_value=0.0)

    # Calcul du débit massique de vapeur
    if st.button("Calculer débit vapeur VP1 - ECH EA"):
        try:
                delta_T1 = T_VP1 - T_ee
                delta_T2 = T_VP1 - T_ea

                if delta_T1 > 0 and delta_T2 > 0 and (delta_T1 != delta_T2):
                    LMTD = (delta_T1 - delta_T2) / math.log(delta_T1 / delta_T2)
                    m_VP1 = ((H * S * LMTD) / (h_VP1 - h_CDS) )/3600
                

                    st.success(f"🔹Débit vapeur entrante VP1 calculé = {m_VP1:.2f} t/h")
                    st.success(f"🔹Débit des condensats= {m_VP1:.2f} t/h")

                    # Enregistrement des résultats
                    st.session_state["resultats_machines"]["ECH EA"] = {
                        "VP1": m_VP1,
                        "CDS": m_VP1
                    }
                else:
                    st.warning("Vérifiez que Température(VP1) > Température(eau) et Température(VP1) > Température(eau adoucie), et que Température(eau) ≠ Température(eau adoucie).")
        except ZeroDivisionError:
                st.error("Erreur de division par zéro dans le calcul du logarithme.")
        except Exception as e:
                st.error(f"Erreur inattendue : {e}")

def bilan_echangeur_ED():
    st.header("Bilan de l'échangeur d'eaux déminéralisées ")
    st.info("Saisissez les données des entrées et sorties de votre machine : Enthalpies, Températures, coefficient d'échange et surface d'échange.")

    # Saisie des paramètres
    H = st.number_input("Coefficient d'échange thermique H (W/m²·K)", min_value=0.0)
    S = st.number_input("Surface d'échange S (m²)", min_value=0.0)

    T_ee = st.number_input("Température de l'eau entrant (°C)", min_value=0.0)
    T_ed = st.number_input("Température de l'eau déminéralisée sortante (°C) ", min_value=0.0)

    T_VP1 = st.number_input("Température de la vapeur VP1  (°C)", min_value=0.0)

    h_VP1 = st.number_input("Enthalpie vapeur VP1  (kJ/kg)", min_value=0.0)
    h_CDS = st.number_input("Enthalpie des condensats (kJ/kg)", min_value=0.0)

    # Calcul du débit massique de vapeur
    if st.button("Calculer débit vapeur VP1 - ECH ED"):
        try:
            delta_T1 = T_VP1 - T_ee
            delta_T2 = T_VP1 - T_ed

            if delta_T1 > 0 and delta_T2 > 0 and (delta_T1 != delta_T2):
                LMTD = (delta_T1 - delta_T2) / math.log(delta_T1 / delta_T2)
                m_VP1 = ((H * S * LMTD) / (h_VP1 - h_CDS) )/3600
            

                st.success(f"🔹Débit vapeur entrante VP1 calculé = {m_VP1:.2f} t/h")
                st.success(f"🔹Débit des condensats= {m_VP1:.2f} t/h")

                # Enregistrement des résultats
                st.session_state["resultats_machines"]["ECH ED"] = {
                    "VP1": m_VP1,
                    "CDS": m_VP1
                }
            else:
                st.warning("Vérifiez que Température(VP1) > Température(eau) et Température(VP1) > Température(eau déminéralisée), et que Température(eau) ≠ Température(eau démineralisée).")
        except ZeroDivisionError:
            st.error("Erreur de division par zéro dans le calcul du logarithme.")
        except Exception as e:
            st.error(f"Erreur inattendue : {e}")



def bilan_echangeur_2400():
    st.header("Bilan de l'échangeur 2400 ")
    st.info("Saisissez les données des entrées et sorties de votre machine : Enthalpies, Températures, coefficient d'échange et surfaces d'échange.")
    
        # Saisie des paramètres
    H = st.number_input("Coefficient d'échange thermique H (W/m²·K)", min_value=0.0)
    S1 = st.number_input("Surface d'échange avec la VP1 (m²)", min_value=0.0, value=100.0)
    S2 = st.number_input("Surface d'échange avec la VPT (m²)", min_value=0.0, value=300.0)
    T_sn = st.number_input("Température du sirop entrant (non chauffé) (°C)", min_value=0.0)
    T_s = st.number_input("Température sirop sortant (chauffé) (°C)", min_value=0.0)

    T_VP1 = st.number_input("Température de la vapeur VP1  (°C)", min_value=0.0)
    T_VPT = st.number_input("Température de la vapeur VPT  (°C)", min_value=0.0)
    
    h_VP1 = st.number_input("Enthalpie vapeur VP1  (kJ/kg)", min_value=0.0)
    h_CDS1 = st.number_input("Enthalpie des condensats VP1 (kJ/kg)", min_value=0.0)
    h_VPT = st.number_input("Enthalpie vapeur VPT  (kJ/kg)", min_value=0.0)
    h_CDST = st.number_input("Enthalpie des condensats VPT(kJ/kg)", min_value=0.0)

    # Calcul du débit massique de vapeur
    if st.button("Calculer débit vapeur VP1 & VPT - ECH 2400"):
        try:
            delta_T11 = T_VP1 - T_sn
            delta_T21 = T_VP1 - T_s
            delta_T1T = T_VPT - T_sn
            delta_T2T = T_VPT - T_s

            if delta_T11 > 0 and delta_T21 > 0 and (delta_T11 != delta_T21) and delta_T1T > 0 and delta_T2T > 0 and (delta_T1T != delta_T2T) :
                LMTD1 = (delta_T11 - delta_T21) /(math.log(delta_T11 / delta_T21))
                LMTDT = (delta_T1T - delta_T2T) / (math.log(delta_T1T / delta_T2T))
                m_VP1 = ((H * S1 * LMTD1) / (h_VP1 - h_CDS1))/3600
                m_VPT = ((H * S2 * LMTDT) / (h_VPT - h_CDST))/3600
            

                st.success(f"🔹Débit vapeur entrante VP1 calculé = {m_VP1:.2f} t/h")
                st.success(f"🔹Débit vapeur entrante VPT calculé = {m_VPT:.2f} t/h")
                st.success(f"🔹Débit des condensats VP1 = {m_VP1:.2f} t/h")
                st.success(f"🔹Débit des condensats VPT = {m_VPT:.2f} t/h")

                # Enregistrement des résultats
                st.session_state["resultats_machines"]["ECH 2400"] = {
                    "VP1": m_VP1,
                    "VPT": m_VPT,
                    "CDS(VP1)": m_VP1,
                    "CDS(VPT)": m_VPT
                }
            else:
                st.warning("Vérifiez que Température(VP1) > Température(eau) et Température(VP1) > Température(eau déminéralisée), et que Température(eau) ≠ Température(eau démineralisée).")
        except ZeroDivisionError:
            st.error("Erreur de division par zéro dans le calcul du logarithme.")
        except Exception as e:
            st.error(f"Erreur inattendue : {e}")

#########################################################################################################
def bilan_dch_f2():
    st.header("Bilan du DCH du fondoir F2")
    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, débit volumiques")
   
    h_VP1 = st.number_input("Enthalpie vapeur VP1", min_value=0.0)

    Q_SF1 = st.number_input("Débit du sirop à la sortie F1  (m³/h)", min_value=0.0)
    T_SF1 = st.number_input("Température du sirop à la sortie F1  (°C)", min_value=0.0)
    Brix_SF1 = st.number_input("Brix du sirop à la sortie F1  (%)", min_value=0.0, max_value=100.0)

    Q_SF2 = st.number_input("Débit du sirop sortant vers F2 (m³/h)", min_value=0.0)
    T_SF2 = st.number_input("Température du sirop sortant vers F2   (°C)", min_value=0.0)
    Brix_SF2 = st.number_input("Brix du sirop sortant vers F2 (%)", min_value=0.0, max_value=100.0)

    if st.button("Calculer VP1 - DCH F2"):
        try:
            Cp_SF1 = Cp(Brix_SF1)
            Cp_SF2 = Cp(Brix_SF2)
            m_SF2=Q_SF2 * D(Brix_SF2)
            m_SF1=Q_SF1 * D(Brix_SF1)
            numerator = m_SF2 * Cp_SF2 * T_SF2 - m_SF1 * Cp_SF1 * T_SF1
            denominator = h_VP1

            if denominator == 0:
                st.error("Erreur : division impossible.")
                return

            m_VP1 = numerator / denominator

            st.success(f"🔹Débit vapeur entrante VP1 calculé = {m_VP1:.2f} t/h")
            # Enregistrement dans session_state
            st.session_state["resultats_machines"]["DCH Fondoir F2"] = {
                "VP1": m_VP1
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")

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

        vapeur_consommée =  VP2_F0 + VP2_F1 + VP2_ES
        vapeur_condenseur = VP2_CEFT - vapeur_consommée

        # Affichage
        st.write(f"🔸 Vapeur CEFT 1600 (VP2) = {VP2_CEFT:.2f} t/h")
        st.write(f"🔸 Vapeur consommée par DCHs = {vapeur_consommée:.2f} t/h")
        st.success(f"🔹 Débit de vapeur arrivant au condenseur = {vapeur_condenseur:.2f} t/h")

        # Enregistrement
        st.session_state["resultats_machines"]["Condenseur"] = {
            "Débit vapeur entrante": vapeur_condenseur
        }

        if abs(vapeur_condenseur) < 0.1:
            st.warning("💡 Le débit est très faible, ce qui confirme que toute la vapeur a été consommée.")

    except Exception as e:
        st.error(f"Erreur dans le calcul du condenseur : {e}")


##############################################################################
def bilan_vkt():

    st.header("Bilan de la tour de cristallisation VKT")
    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, volume entrant, débit volumiques")
    
    h_VP1 = st.number_input("Enthalpie vapeur VP1 (kJ/kg)", min_value=0.0)
    h_CDS = st.number_input("Enthalpie des condensats (kJ/kg)", min_value=0.0)
    h_Eevap = st.number_input("Enthalpie de l'eau évaporée (kJ/kg)", min_value=0.0)

    T_SC = st.number_input("Température du sirop concentré entrant (°C)", min_value=0.0)
    Brix_SC = st.number_input("Brix du sirop concentré entrant (%)", min_value=0.0, max_value=100.0)

    V_MC = st.number_input("Volume sortant de la masse cuite (m³)", min_value=0.0)
    T_MC = st.number_input("Température de la masse cuite (°C)", min_value=0.0)
    Brix_MC = st.number_input("Brix de la masse cuite (%)", min_value=0.0, max_value=100.0)

   

    if st.button("Calculer VP1 - VKT"):
        try:
            Cp_SC = Cp(Brix_SC)
            Cp_MC = Cp(Brix_MC)
            D_SC = D(Brix_SC)
            D_MC = D(Brix_MC)

        # Le bilan matière
            V_SC = (D_MC * V_MC * (Brix_MC)/100)/(D_SC * (Brix_SC)/100)
            m_SC = D_SC * V_SC * (Brix_SC)/100
            m_MC = D_MC * V_MC * (Brix_MC)/100
            m_Eevap = V_SC - V_MC


            numerator = m_Eevap * h_Eevap + m_MC * Cp_MC * T_MC - m_SC * Cp_SC * T_SC
            denominator = h_VP1 - h_CDS

            if denominator == 0:
                st.error("Erreur : h_VP1 et h_CDS sont égaux → division impossible.")
                return

            m_VP1 = numerator / denominator
            m_CDS = m_VP1  # Hypothèse : condensation totale

            st.success(f"🔹Débit vapeur entrante VP1 calculé = {m_VP1:.2f} t/h") 
            st.success(f"🔹Débit des condensats = {m_CDS:.2f} t/h")
            st.success(f"🔹Débit de l'eau évaporée calculé = {m_Eevap:.2f} t/h")
            st.success(f"🔹Volume du sirop entrant calculé = {V_SC:.2f} t/h")

            st.session_state["resultats_machines"]["VKT"] = {
                "VP1" : m_VP1,
                "CDS": m_CDS,
                "Eau évaporée": m_Eevap,
                "Volume entrant" : V_SC,

            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")

####################################################################
def bilan_CMV():
    st.header("Bilan du compresseur mécanique à vapeur CMV")
    st.info("Saisissez les données des entrées et sorties de votre machine : Enthalpies  et travail ")

    W_Vvkt =st.number_input("Travail des CMV (KW)", min_value=0.0)
    h_Vvkt = st.number_input("Enthalpie de la vapeur sortante de la VKT (KJ/Kg)", min_value=0.0)
    h_VPcomp = st.number_input("Enthalpie de la vapeur comprimée (KJ/Kg)", min_value=0.0)

    if st.button("Calculer Vvkt - CMV"):
        try:
            numerator = W_Vvkt
            denominator = h_VPcomp - h_Vvkt

            if denominator == 0:
                st.error("Erreur : division impossible.")
                return

            m_Vvkt = numerator / denominator
        
            st.success(f"🔹Débit vapeur entrante VPT calculé = {m_Vvkt:.2f} t/h")
            
            # Enregistrement dans session_state
            st.session_state["resultats_machines"]["DCH ES"] = {
                "Vvkt": m_Vvkt
            }
        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")

#######################################################################################

def bilan_carbo():
    st.header("Bilan de l'échangeur sécheur")
    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, débit volumiques")

    h_VPT = st.number_input("Enthalpie vapeur VPT (kJ/kg)", min_value=0.0)

    Q_FC = st.number_input("Débit de la fonte commune entrante (m³/h)", min_value=0.0)
    T_FC = st.number_input("Température de la fonte commune entrante (°C)", min_value=0.0)
    Brix_FC = st.number_input("Brix de la fonte commune entrante (%)", min_value=0.0, max_value=100.0, value=100.0)

    Q_FCa = st.number_input("Débit de la fonte carbonaté sortante (m³/h)", min_value=0.0)
    T_FCa = st.number_input("Température de la fonte carbonaté sortante (°C)", min_value=0.0)
    Brix_FCa = st.number_input("Brix de la fonte carbonaté sortante (%)", min_value=0.0, max_value=100.0, value=100.0)

    h_CDS = st.number_input("Enthalpie des condensats (kJ/kg)", min_value=0.0)


    if st.button("Calculer VPT - Station de carbonatation"):
        try:
            Cp_FC = Cp(Brix_FC)
            Cp_FCa = Cp(Brix_FCa)
            m_FCa=Q_FCa * D(Brix_FCa)
            m_FC=Q_FC * D(Brix_FC)

            numerator = m_FCa * Cp_FCa * T_FCa - m_FC * Cp_FC * T_FC
            denominator = h_VPT - h_CDS

            if denominator == 0:
                st.error("Erreur : enthalpie vapeur VPT = 0 → division impossible.")
                return

            m_VPT = numerator / denominator
            m_CDS = m_VPT

            st.success(f"🔹Débit vapeur entrante VPT calculé = {m_VPT:.2f} t/h")

            # Enregistrement dans session_state
            st.session_state["resultats_machines"]["Station de carbonatation"] = {
                "VPT": m_VPT,
                "CDS": m_CDS
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")












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
            V_SC = (D_MC * V_MC * (Brix_MC)/100)/D_SC * (Brix_SC)/100
            m_SC = D_SC * V_SC * (Brix_SC)/100
            m_MC = D_MC * V_MC * (Brix_MC)/100
            m_Eevap = V_SC - V_MC


            numerator = m_Eevap * h_Eevap + m_MC * Cp_MC * T_MC - m_SC * Cp_SC * T_SC
            denominator = h_VPT - h_CDS

            if denominator == 0:
                st.error("Erreur : h_VPT et h_CDS sont égaux → division impossible.")
                return

            m_VPT = numerator / denominator
            m_CDS = m_VPT  # Hypothèse : condensation totale

            st.success(f"🔹Débit vapeur entrante VPT calculé = {m_VPT:.2f} t/h")
            st.success(f"🔹Débit des condensats = {m_CDS:.2f} t/h")
            st.success(f"🔹Débit de l'eau évaporée calculé = {m_Eevap:.2f} t/h")
            st.success(f"🔹Volume du sirop entrant calculé = {V_SC:.2f} m^3")

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
            V_SC = (D_MC * V_MC * (Brix_MC)/100)/D_SC * (Brix_SC)/100
            m_SC = D_SC * V_SC * (Brix_SC)/100
            m_MC = D_MC * V_MC * (Brix_MC)/100
            m_Eevap = V_SC - V_MC


            numerator = m_Eevap * h_Eevap + m_MC * Cp_MC * T_MC - m_SC * Cp_SC * T_SC
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


            numerator = m_Eevap * h_Eevap + m_MC * Cp_MC * T_MC - m_SC * Cp_SC * T_SC
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
                "VP1": m_VPT,
                "CDS": m_CDS,
                "Eau évaporée": m_Eevap,
                "Volume entrant du sirop" : V_SC

            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")
###################################################################
def bilan_ECH_sécheur():
    st.header("Bilan de l'échangeur sécheur")
    st.info("Saisissez les données des entrées et sorties de votre machine : Températures, Brix, enthalpies, débit volumiques")

    h_VPT = st.number_input("Enthalpie vapeur VPT (kJ/kg)", min_value=0.0)

    Q_SHe = st.number_input("Débit du sucre non séché (m³/h)", min_value=0.0)
    T_SHe = st.number_input("Température du sucre non séché (°C)", min_value=0.0)
    Brix_SHe = st.number_input("Brix du sucre non séché (%)", min_value=0.0, max_value=100.0, value=100.0)

    Q_SHs = st.number_input("Débit du sucre séché (m³/h)", min_value=0.0)
    T_SHs = st.number_input("Température du sucre séché (°C)", min_value=0.0)
    Brix_SHs = st.number_input("Brix du sucre séché (%)", min_value=0.0, max_value=100.0, value=100.0)

    h_CDS = st.number_input("Enthalpie des condensats (kJ/kg)", min_value=0.0)


    if st.button("Calculer VPT - ECH Sécheur"):
        try:
            Cp_SHs = Cp(Brix_SHs)
            Cp_SHe = Cp(Brix_SHe)
            m_SHs=Q_SHs * D(Brix_SHs)
            m_SHe=Q_SHe * D(Brix_SHe)

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

    T_MCvkt = st.session_state["resultats_machines"]["VKT"].get("T_MC", 0.0)
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
            numerator = m_Eevap * h_Eevap + m_MCs * Cp_MCs * T_MCs - m_MCvkt * Cp_MCvkt * T_MCvkt
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
                "Vapeur comprimée": m_VPc,
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
            numerator = m_Eevap * h_Eevap + m_MCR32 * Cp_MCR32 * T_MCR32 - m_MCR31 * Cp_MCR31 * T_MCR31
            denominator = h_VPc - h_CDS

            if denominator == 0:
                st.error("Erreur : h_VPc et h_CDS sont égaux → division impossible.")
                return

            m_VPc = numerator / denominator
            m_CDS = m_VPc  # Hypothèse : condensation totale

            st.success(f"💨 Débit vapeur VPc estimé : {m_VPc:.2f} kg/h")
            st.write(f"Eau évaporée = {m_Eevap:.2f} kg/h")
            st.write(f"Volume entrant = {V_MCR31:.2f} kg/h")
            st.write(f"Condensats = {m_CDS:.2f} kg/h")

            st.session_state["resultats_machines"]["Cuite R32"] = {
                "Vapeur comprimée": m_VPc,
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
            numerator = m_Eevap * h_Eevap + m_MCR4 * Cp_MCR4 * T_MCR4 - m_MCR32 * Cp_MCR32 * T_MCR32
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
                "Vapeur comprimée": m_VPc,
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
            numerator = m_Eevap * h_Eevap + m_MCA * Cp_MCA * T_MCA - m_MCR4 * Cp_MCR4 * T_MCR4 
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
                "Vapeur comprimée": m_VPc,
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
            numerator = m_Eevap * h_Eevap + m_MCB * Cp_MCB * T_MCB - m_MCA * Cp_MCA * T_MCA 
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
                "Vapeur comprimée": m_VPc,
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


    if st.button("Calculer VPc - Cuite B"):
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
            numerator = m_Eevap * h_Eevap + m_MCC * Cp_MCC * T_MCC - m_MCB * Cp_MCB * T_MCB 
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
                "Vapeur comprimée": m_VPc,
                "CDS": m_CDS,
                "Eau évaporée": m_Eevap,
                "Volume entrant de la masse cuite": V_MCB
            }

        except Exception as e:
            st.error(f"Erreur dans le calcul : {e}")



def bilan_divers():
    st.header("Bilan de la machine Divers")

    try:
        # Débit vapeur produite par le Bouilleur
        m_VPT_bouilleur = st.session_state["resultats_machines"]["Bouilleur"]["VPT"]
    except KeyError:
        st.error("Le débit VPT du Bouilleur n'est pas encore disponible.")
        return

    # Récupérer tous les débits VPT consommés par les machines (hors Bouilleur et Divers)
    m_VPT_consommée = 0.0
    for machine, resultats in st.session_state["resultats_machines"].items():
        if machine not in ["Bouilleur", "Divers"]:
            if "VPT" in resultats:
                m_VPT_consommée += resultats["VPT"]

    # Calcul du débit de la machine Divers
    m_VPT_divers = m_VPT_bouilleur - m_VPT_consommée

    # Affichage du résultat
    st.markdown(f"### 🔹 Débit de vapeur VPT attribué à la machine Divers : **{m_VPT_divers:.2f} t/h**")

    # Enregistrement dans les résultats
    st.session_state["resultats_machines"]["Divers"] = {
        "VPT": m_VPT_divers
    }








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
    "ECH EA" : bilan_echangeur_EA,
    "ECH ED" : bilan_echangeur_ED,
    "ECH 2400" : bilan_echangeur_2400,
    "DCH Fondoir F0" : bilan_dch_f0,
    "DCH Fondoir F1" : bilan_dch_f1,
    "DCH Fondoir F2" : bilan_dch_f2,
    "DCH des eaux sucrées ES": bilan_dch_ES,
    "Condenseur": bilan_condenseur,
    "VKT": bilan_vkt,
    "CMV" : bilan_CMV,
    "Station de carbonatation" : bilan_carbo ,
    "Cuite 710HL" : bilan_cuite710,
    "Cuite 550HL" : bilan_cuite550,
    "R2" : bilan_cuiteR2,
    "ECH sécheur" : bilan_ECH_sécheur,
    "R31" : bilan_cuiteR31,
    "R32" : bilan_cuiteR32,
    "R4" : bilan_cuiteR4,
    "A" : bilan_cuiteA,
    "B" : bilan_cuiteB,
    "C" : bilan_cuiteC,
    "Divers machines restantes" :bilan_divers,
}

# Sélection de la machine
selected_machine = st.selectbox("🔧 Choisissez une machine :", machines)

if selected_machine:
    if selected_machine in bilan_machines:
        bilan_machines[selected_machine]()
    else:
        st.info("Pas encore de bilan défini pour cette machine.")

if "CEFT 1600" in st.session_state["resultats_machines"]:
            comparer_vp1()

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
        "ECH EA": "VP1",
        "ECH ED": "VP1",
        "DCH Fondoir F2": "VP1",
        "VKT": "VP1",
        "ECH 2400": "VPT",
        "DCH Fondoir F0": "VP2",
        "DCH Fondoir F1": "VP2",
        "DCH des eaux sucrées ES": "VP2",
        "CMV": "Vvkt",
        "Cuite 710HL": "VPT",
        "Cuite 550HL": "VPT",
        "R2": "VPT",
        "Echangeur sécheur" : "VPT",
        "Station de carbonatation" :"VPT",
        "R31": "Vvkt",
        "R32": "Vvkt",
        "R4": "Vvkt",
        "A": "Vvkt",
        "B": "Vvkt",
        "C": "Vvkt"
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

def afficher_pie_charts_par_vapeur(groupes):
    for vapeur, machines in groupes.items():
        labels = []
        valeurs = []

        for machine, donnees in machines.items():
            # Vérifie que la clé débit vapeur existe
            if "Débit vapeur (kg/h)" in donnees and donnees["Débit vapeur (kg/h)"] > 0:
                labels.append(machine)
                valeurs.append(donnees["Débit vapeur (kg/h)"])

        if labels and valeurs:
            fig, ax = plt.subplots()
            ax.pie(valeurs, labels=labels, autopct="%1.1f%%", startangle=90)
            ax.set_title(f"Répartition des débits vapeur - {vapeur}")
            st.pyplot(fig)
        else:
            st.warning(f"Aucune donnée à afficher pour la vapeur : {vapeur}")

# Appel de ta fonction de regroupement
groupes = regroupement_par_vapeur(st.session_state["resultats_machines"])

# Affichage de tous les diagrammes circulaires
afficher_pie_charts_par_vapeur(groupes)

def creer_pie_chart(labels, sizes, title):
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    plt.title(title)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
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
                pdf.cell(0, 8, f"{nom_debit} = {valeur:.2f} kg/h", ln=True)
            pdf.ln(2)

            # Récupérer la valeur pour cette vapeur pour le pie chart
            valeur_machine_pour_vapeur = resultats.get(vapeur, 0)
            if valeur_machine_pour_vapeur > 0:
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
