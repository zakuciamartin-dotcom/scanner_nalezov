import streamlit as st
import pytesseract
from PIL import Image
import re
import pandas as pd

st.set_page_config(page_title="Pľúcny Scanner", layout="wide")
st.title("🫁 Inteligentný pľúcny extraktor")

TARGET_VALUES = [
    "FVCEx", "FEV1", "FEV1/FVC", "TLC", "TGV", 
    "RV", "RV/TLC", "sRefftot", "TLco(Hb)", "Kco(Hb)", "VA"
]

img_file = st.file_uploader("Nahrajte fotku nálezu alebo odfoťte", type=['jpg', 'jpeg', 'png'])

if not img_file:
    img_file = st.camera_input("Alebo odfoťte priamo")


if img_file:
    with st.spinner('Analyzujem štruktúru tabuľky...'):
        img = Image.open(img_file)
        # Spracovanie textu s dôrazom na riadky
        raw_text = pytesseract.image_to_string(img, config='--psm 6')
        
        extracted_data = []

        for key in TARGET_VALUES:
            # REGEX VYSVETLENIE:
            # 1. Hľadáme názov (napr. FVCEx)
            # 2. Preskočíme jednotky a zátvorky (všetko až po prvé hlavné číslo)
            # 3. Zachytíme 3 hlavné číselné stĺpce (Pre, %Nál, Z-skóre)
            
            # Tento regex hľadá: Názov -> hocičo -> číslo(Pre) -> hocičo -> číslo(%Nál) -> hocičo -> číslo(Z-skóre)
            pattern = re.compile(
                re.escape(key) + 
                r".+?(\d+[\.,]\d+)" +  # 1. stĺpec (Pre)
                r".+?(\d+[\.,]\d+)" +  # 2. stĺpec (%Nál.)
                r".+?([\d\-\.,]+)"     # 3. stĺpec (Z-skóre - môže byť aj záporné)
            )
            
            match = pattern.search(raw_text)
            
            if match:
                extracted_data.append({
                    "Parameter": key,
                    "Pre": match.group(1),
                    "%Nál.": match.group(2),
                    "Z-skóre": match.group(3)
                })

        if extracted_data:
            df = pd.DataFrame(extracted_data)
            st.table(df)
            
            # Formát pre kopírovanie
            st.subheader("Text na skopírovanie")
            copy_string = ""
            for d in extracted_data:
                copy_string += f"{d['Parameter']}\t{d['Pre']}\t{d['%Nál.']}\t{d['Z-skóre']}\n"
            st.text_area("Skopírujte do Excelu/Správy:", copy_string, height=200)
        else:
            st.warning("Nepodarilo sa nájsť hodnoty. Skúste odfotiť detailnejšie.")

st.info("💡 Tento skener automaticky preskakuje stĺpce s jednotkami a referenčnými normami v zátvorkách.")
