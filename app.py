import streamlit as st
import pandas as pd
import io

# Настройка страницы
st.set_page_config(
    page_title="Анализатор URL",
    page_icon="🔍",
    layout="wide"
)

# Заголовок приложения
st.title("🔍 Анализатор URL")
st.markdown("---")

# Создаем три колонки для полей
col1, col2, col3 = st.columns([1, 1, 1])

# ПОЛЕ 1: Загрузка Excel файла с URL
with col1:
    st.subheader("📁 Загрузка Excel файла")
    st.write("Загрузите файл Excel с URLs")
    
    uploaded_file = st.file_uploader(
        "Выберите Excel файл", 
        type=['xlsx', 'xls'],
        key="excel_uploader"
    )
    
    excel_urls = []
    
    if uploaded_file is not None:
        try:
            # Читаем Excel файл
            df = pd.read_excel(uploaded_file)
            
            # Показываем информацию о файле
            st.success(f"✅ Файл успешно загружен!")
            st.write(f"Колонки в файле: {list(df.columns)}")
            
            # Выбираем колонку для анализа (первая по умолчанию)
            if len(df.columns) > 0:
                column_to_use = st.selectbox(
                    "Выберите колонку с URLs:",
                    options=list(df.columns),
                    index=0
                )
                
                # Извлекаем URLs из выбранной колонки
                excel_urls = df[column_to_use].dropna().astype(str).tolist()
                
                st.info(f"📊 Найдено URL в файле: **{len(excel_urls)}**")
                
                # Показываем первые 5 URL из файла
                with st.expander("👀 Показать URLs из файла"):
                    for i, url in enumerate(excel_urls[:10], 1):
                        st.write(f"{i}. {url}")
                    if len(excel_urls) > 10:
                        st.write(f"... и еще {len(excel_urls) - 10} URLs")
                        
        except Exception as e:
            st.error(f"❌ Ошибка при чтении файла: {str(e)}")

# ПОЛЕ 2: Ручной ввод URLs
with col2:
    st.subheader("✍️ Ручной ввод URLs")
    st.write("Добавьте URLs для проверки")
    
    # Инициализация списка URLs в session_state
    if 'manual_urls' not in st.session_state:
        st.session_state.manual_urls = [""]
    
    # Функции для управления списком
    def add_url():
        st.session_state.manual_urls.append("")
    
    def remove_url(index):
        if len(st.session_state.manual_urls) > 1:
            st.session_state.manual_urls.pop(index)
    
    def update_url(index, value):
        st.session_state.manual_urls[index] = value
    
    # Отображаем поля для ввода URLs
    for i, url in enumerate(st.session_state.manual_urls):
        col_input, col_btn = st.columns([4, 1])
        
        with col_input:
            new_url = st.text_input(
                f"URL {i+1}",
                value=url,
                key=f"url_{i}",
                placeholder="https://example.com",
                on_change=lambda i=i: update_url(i, st.session_state[f"url_{i}"])
            )
        
        with col_btn:
            if len(st.session_state.manual_urls) > 1:
                st.button("🗑️", key=f"remove_{i}", on_click=remove_url, args=(i,))
    
    # Кнопка добавления нового поля
    st.button("➕ Добавить еще URL", on_click=add_url)
    
    # Подсчет введенных URLs
    valid_manual_urls = [url for url in st.session_state.manual_urls if url.strip()]
    st.info(f"📝 Введено URLs: **{len(valid_manual_urls)}**")

# ПОЛЕ 3: Результаты сравнения
with col3:
    st.subheader("📊 Результаты сравнения")
    st.write("URLs из ручного ввода, которые есть в Excel файле")
    
    if uploaded_file is not None and excel_urls:
        valid_manual_urls = [url.strip() for url in st.session_state.manual_urls if url.strip()]
        
        if valid_manual_urls:
            # Нормализуем URLs для сравнения (убираем пробелы, приводим к нижнему регистру)
            excel_urls_normalized = [url.strip().lower() for url in excel_urls]
            manual_urls_normalized = [url.strip().lower() for url in valid_manual_urls]
            
            # Ищем совпадения
            found_urls = []
            not_found_urls = []
            
            for manual_url in valid_manual_urls:
                if manual_url.strip().lower() in excel_urls_normalized:
                    found_urls.append(manual_url)
                else:
                    not_found_urls.append(manual_url)
            
            # Показываем результаты
            if found_urls:
                st.success(f"✅ Найдено совпадений: **{len(found_urls)}**")
                
                with st.expander("📋 Показать найденные URLs"):
                    for i, url in enumerate(found_urls, 1):
                        st.write(f"{i}. {url}")
            else:
                st.warning("🔍 Совпадений не найдено")
            
            if not_found_urls:
                st.error(f"❌ Не найдено в файле: **{len(not_found_urls)}**")
                
                with st.expander("👀 Показать отсутствующие URLs"):
                    for i, url in enumerate(not_found_urls, 1):
                        st.write(f"{i}. {url}")
        else:
            st.info("📝 Введите URLs во втором поле для проверки")
    else:
        if uploaded_file is None:
            st.info("📁 Загрузите Excel файл в первом поле")
        else:
            st.info("📊 В файле нет данных для сравнения")

# Разделитель
st.markdown("---")

# Дополнительная информация
st.subheader("ℹ️ Инструкция по использованию:")

instructions = """
1. **Поле 1 📁**: Загрузите Excel файл с URLs (поддерживаются .xlsx и .xls)
2. **Поле 2 ✍️**: Добавляйте URLs для проверки (кнопка "➕ Добавить еще URL")
3. **Поле 3 📊**: Автоматически покажет какие URLs из второго поля есть в Excel файле

**Примечания:**
- Сравнение не чувствительно к регистру
- Учитываются пробелы в начале и конце URLs
- Можно добавлять неограниченное количество URLs для проверки
"""

st.markdown(instructions)

# Стили для улучшения внешнего вида
st.markdown("""
<style>
    .stButton button {
        width: 100%;
    }
    .stDownloadButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)