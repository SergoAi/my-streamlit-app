import streamlit as st
import pandas as pd
import io

# Проверка зависимостей
try:
    import openpyxl
except ImportError:
    st.error("❌ Ошибка: Не установлен openpyxl. Добавьте 'openpyxl' в файл requirements.txt")
    st.stop()

# Настройка страницы
st.set_page_config(
    page_title="Анализатор URL",
    page_icon="🔍",
    layout="wide"
)

# Заголовок приложения
st.title("🔍 Анализатор URL")
st.markdown("---")

# Инициализация session_state
if 'manual_urls' not in st.session_state:
    st.session_state.manual_urls = [""]

# Функции для управления URLs
def add_url():
    st.session_state.manual_urls.append("")

def remove_url(index):
    if len(st.session_state.manual_urls) > 1:
        st.session_state.manual_urls.pop(index)

# Создаем три колонки
col1, col2, col3 = st.columns([1, 1, 1])

# ПОЛЕ 1: Загрузка Excel файла
with col1:
    st.subheader("📁 Загрузка Excel файла")
    uploaded_file = st.file_uploader("Выберите Excel файл", type=['xlsx', 'xls'])
    
    excel_urls = []
    if uploaded_file is not None:
        try:
            # Читаем Excel файл
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            st.success(f"✅ Файл загружен! Колонки: {list(df.columns)}")
            
            if len(df.columns) > 0:
                column_to_use = st.selectbox("Выберите колонку с URLs:", options=list(df.columns))
                excel_urls = df[column_to_use].dropna().astype(str).tolist()
                st.info(f"📊 Найдено URL: {len(excel_urls)}")
                
                # Показываем первые URLs
                with st.expander("👀 Показать URLs из файла"):
                    for i, url in enumerate(excel_urls[:5], 1):
                        st.write(f"{i}. {url}")
                    if len(excel_urls) > 5:
                        st.write(f"... и еще {len(excel_urls) - 5} URLs")
                        
        except Exception as e:
            st.error(f"❌ Ошибка при чтении файла: {str(e)}")

# ПОЛЕ 2: Ручной ввод URLs
with col2:
    st.subheader("✍️ Ручной ввод URLs")
    st.write("Добавляйте URLs для проверки:")
    
    # Обновляем URLs в session_state
    for i in range(len(st.session_state.manual_urls)):
        st.session_state.manual_urls[i] = st.text_input(
            f"URL {i+1}",
            value=st.session_state.manual_urls[i],
            key=f"url_{i}",
            placeholder="https://example.com"
        )
    
    # Кнопки управления
    col_add, col_info = st.columns([1, 2])
    with col_add:
        st.button("➕ Добавить URL", on_click=add_url)
    with col_info:
        valid_urls = [url for url in st.session_state.manual_urls if url.strip()]
        st.info(f"📝 Введено: {len(valid_urls)} URL")
    
    # Кнопки удаления (если больше 1 URL)
    if len(st.session_state.manual_urls) > 1:
        st.write("Удалить URL:")
        cols = st.columns(min(3, len(st.session_state.manual_urls)))
        for i in range(len(st.session_state.manual_urls)):
            with cols[i % 3]:
                if st.button(f"🗑️ URL {i+1}", key=f"del_{i}"):
                    remove_url(i)
                    st.rerun()

# ПОЛЕ 3: Результаты сравнения
with col3:
    st.subheader("📊 Результаты сравнения")
    st.write("URLs из ручного ввода, которые есть в Excel файле:")
    
    if uploaded_file is not None and excel_urls:
        valid_manual_urls = [url.strip() for url in st.session_state.manual_urls if url.strip()]
        
        if valid_manual_urls:
            # Нормализуем для сравнения
            excel_normalized = [url.strip().lower() for url in excel_urls]
            manual_normalized = [url.strip().lower() for url in valid_manual_urls]
            
            # Ищем совпадения
            found_urls = []
            not_found_urls = []
            
            for url in valid_manual_urls:
                if url.strip().lower() in excel_normalized:
                    found_urls.append(url)
                else:
                    not_found_urls.append(url)
            
            # Показываем результаты
            if found_urls:
                st.success(f"✅ Найдено совпадений: {len(found_urls)}")
                with st.expander("📋 Показать найденные URLs"):
                    for url in found_urls:
                        st.write(f"• {url}")
            
            if not_found_urls:
                st.error(f"❌ Не найдено в файле: {len(not_found_urls)}")
                with st.expander("👀 Показать отсутствующие URLs"):
                    for url in not_found_urls:
                        st.write(f"• {url}")
                        
            if not found_urls and not not_found_urls:
                st.warning("🔍 Совпадений не найдено")
        else:
            st.info("📝 Введите URLs для проверки")
    else:
        st.info("📁 Загрузите Excel файл в первом поле")

# Инструкция
st.markdown("---")
st.subheader("ℹ️ Инструкция:")
st.write("""
1. **📁 Загрузите Excel файл** с URLs в первой колонке
2. **✍️ Добавьте URLs** для проверки (кнопка '➕ Добавить URL')
3. **📊 Смотрите результаты** - какие URLs есть в файле
""")

st.success("✅ Все зависимости установлены! Приложение готово к работе.")
