import streamlit as st
import yfinance as yf
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Consulta Avanzada de Activos", layout="centered")
st.title("📊 Consulta de precios, volúmenes y dividendos de activos")
st.markdown("Consulta el precio, volumen negociado y pagos de dividendos de cualquier acción, ETF, bono o cripto compatible con Yahoo Finance.")

# Input del usuario
ticker_input = st.text_input("🔍 Ingresa el ticker (clave de pizarra):", "AAPL")

# Selección de frecuencia
frecuencia = st.selectbox("🕒 Frecuencia de precios:", ["Diaria", "Semanal", "Mensual"])
intervalos = {"Diaria": "1d", "Semanal": "1wk", "Mensual": "1mo"}

# Selección de plazo
plazo = st.selectbox("📅 Plazo:", ["1 día", "1 mes", "3 meses", "6 meses", "12 meses", "5 años", "Máximo disponible"])
plazos = {
    "1 día": "1d", "1 mes": "1mo", "3 meses": "3mo",
    "6 meses": "6mo", "12 meses": "1y", "5 años": "5y",
    "Máximo disponible": "max"
}

# Botón para obtener datos
if st.button("🔽 Obtener datos"):
    try:
        # Consulta de precios y volumen
        ticker = yf.Ticker(ticker_input)
        data = ticker.history(period=plazos[plazo], interval=intervalos[frecuencia])

        # Consulta de dividendos
        dividends = ticker.dividends

        # Verificación de existencia de datos
        if data.empty:
            st.warning("No se encontraron datos para los criterios seleccionados.")
        else:
            # Preparar tabla precios + volumen
            precios_volumen = data[['Close', 'Volume']].rename(columns={
                'Close': 'Precio de Cierre',
                'Volume': 'Volumen'
            })

            st.success(f"✅ Datos obtenidos para {ticker_input}")

            # Mostrar gráfico de precios
            st.subheader("📈 Precio de Cierre")
            st.line_chart(precios_volumen['Precio de Cierre'])

            # Mostrar gráfico de volumen (si aplica)
            if precios_volumen['Volumen'].sum() > 0:
                st.subheader("📊 Volumen Negociado")
                st.bar_chart(precios_volumen['Volumen'])
            else:
                st.info("ℹ️ No hay volumen disponible para este ticker (posiblemente sea un índice, tasa o bono).")

            # Mostrar dividendos si existen
            if not dividends.empty:
                st.subheader("💰 Pagos de Dividendos")
                st.dataframe(dividends.rename("Dividendo Pagado").to_frame())

                # Agregar dividendos al Excel
                precios_volumen.index = precios_volumen.index.tz_localize(None)
                dividends.index = dividends.index.tz_localize(None)
                precios_volumen = precios_volumen.reset_index()
                precios_volumen['Date'] = precios_volumen['Date'].dt.strftime('%d/%m/%Y')
                with pd.ExcelWriter(f"{ticker_input}_datos_completos.xlsx") as writer:
                    precios_volumen.to_excel(writer, sheet_name="Precios y Volumen", index=False)
                    dividends_df.to_excel(writer, sheet_name="Dividendos", index=False)
                    dividends_df = dividends.rename("Dividendo Pagado").to_frame().reset_index()
                    dividends_df['Date'] = dividends_df['Date'].dt.strftime('%d/%m/%Y')                    
                with open(f"{ticker_input}_datos_completos.xlsx", "rb") as f:
                    st.download_button(
                        "📥 Descargar Excel completo (con dividendos)",
                        f,
                        file_name=f"{ticker_input}_datos_completos.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.info("ℹ️ No se encontraron dividendos para este activo.")

    except Exception as e:
        st.error(f"❌ Ocurrió un error: {e}")
