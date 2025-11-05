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
    st.write("Добавляйте URLs или части URLs для поиска:")
    
    # Обновляем URLs в session_state
    for i in range(len(st.session_state.manual_urls)):
        st.session_state.manual_urls[i] = st.text_input(
            f"URL или часть URL {i+1}",
            value=st.session_state.manual_urls[i],
            key=f"url_{i}",
            placeholder="https://example.com или products-chervyachnyj_motor-reduktor_nmrv"
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
    st.write("Найденные URLs из Excel файла:")
    
    if uploaded_file is not None and excel_urls:
        valid_manual_urls = [url.strip() for url in st.session_state.manual_urls if url.strip()]
        
        if valid_manual_urls:
            # Все найденные совпадения
            all_matches = []
            not_found_urls = []
            
            for search_term in valid_manual_urls:
                found_any = False
                
                for excel_url in excel_urls:
                    excel_url_clean = excel_url.strip()
                    search_term_clean = search_term.strip().lower()
                    excel_url_lower = excel_url_clean.lower()
                    
                    # Проверка полного совпадения (не чувствительно к регистру)
                    if excel_url_lower == search_term_clean:
                        all_matches.append({
                            'search_term': search_term,
                            'found_url': excel_url_clean,
                            'match_type': '✅ ПОЛНОЕ СОВПАДЕНИЕ'
                        })
                        found_any = True
                    
                    # Проверка частичного совпадения в любой части URL
                    elif search_term_clean in excel_url_lower:
                        all_matches.append({
                            'search_term': search_term,
                            'found_url': excel_url_clean,
                            'match_type': '🔍 ЧАСТИЧНОЕ СОВПАДЕНИЕ'
                        })
                        found_any = True
                
                # Если ничего не найдено для этого поискового запроса
                if not found_any:
                    not_found_urls.append(search_term)
            
            # Показываем результаты
            
            # Все найденные совпадения
            if all_matches:
                st.success(f"🎯 Найдено совпадений: {len(all_matches)}")
                
                # Группируем по поисковым запросам для удобства
                search_terms_found = set(match['search_term'] for match in all_matches)
                
                for search_term in search_terms_found:
                    with st.expander(f"🔎 Результаты для: `{search_term}`", expanded=True):
                        matches_for_term = [m for m in all_matches if m['search_term'] == search_term]
                        
                        for match in matches_for_term:
                            st.write(f"**Тип совпадения:** {match['match_type']}")
                            st.write(f"**Найденный URL:** {match['found_url']}")
                            st.markdown("---")
            
            # Не найдено
            if not_found_urls:
                st.error(f"❌ Не найдено: {len(not_found_urls)}")
                with st.expander("📝 Показать ненайденные запросы"):
                    for search_term in not_found_urls:
                        st.write(f"• `{search_term}`")
                        
            # Общая статистика
            st.markdown("---")
            full_count = len([m for m in all_matches if m['match_type'] == '✅ ПОЛНОЕ СОВПАДЕНИЕ'])
            partial_count = len([m for m in all_matches if m['match_type'] == '🔍 ЧАСТИЧНОЕ СОВПАДЕНИЕ'])
            
            st.write(f"**📈 Статистика:**")
            st.write(f"• Полных совпадений: {full_count}")
            st.write(f"• Частичных совпадений: {partial_count}")
            st.write(f"• Всего найдено: {len(all_matches)}")
                        
        else:
            st.info("📝 Введите URLs или части URLs для поиска")
    else:
        st.info("📁 Загрузите Excel файл в первом поле")

# Инструкция
st.markdown("---")
st.subheader("ℹ️ Инструкция:")
st.write("""
1. **📁 Загрузите Excel файл** с URLs в выбранной колонке
2. **✍️ Добавьте URLs или части URLs** для поиска:
   - Полный URL: `https://example.com/page.php`
   - Часть URL: `page` (найдет все URLs содержащие "page")
3. **📊 Смотрите результаты** с указанием типа совпадения

**Пример:**
- Поиск: `products-chervyachnyj_motor-reduktor_nmrv`
- Результат: найдет URL `https://cable.ru/reductiongears/products-chervyachnyj_motor-reduktor_nmrv.php`
- Тип: 🔍 ЧАСТИЧНОЕ СОВПАДЕНИЕ
""")

st.success("✅ Приложение готово к работе!")
