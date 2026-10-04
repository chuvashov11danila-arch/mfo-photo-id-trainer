import psycopg2
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()
def clean_text(text):
    if text is None:
        return ""
    t = str(text).strip().lower()
    t = t.replace("гор.", "").replace("г.", "").replace("г-да.", "").replace("город", "")
    t = t.replace("обл.", "").replace("область", "")
    t = t.replace("д.", "").replace("дер.", "").replace("деревня", "")
    t = t.replace("п.", "").replace("пос.", "").replace("посёлок", "") 
    t = t.replace("р.п.", "").replace("рп", "").replace("рабочий посёлок", "")
    t = t.replace("х.", "").replace("хут.", "").replace("х-р", "").replace("хутор", "")
    t = t.replace("р-н.", "").replace("р-он.", "").replace("район", "")
    t = t.replace("ст.", "").replace("станица", "")
    t = t.replace("с.", "").replace("сел.", "").replace("село", "")
    t = t.replace("пгт.", "").replace("посёлок городского типа", "")
    t = t.replace("респ.", "").replace("р-ка", "").replace("республика", "")
    t = t.replace("кор.", "").replace("корп.", "").replace("корпус", "")
    t = t.replace("гор.", "").replace("г.", "").replace("г-да", "").replace("город", "")
    t = t.replace("р.", "").replace("рф", "").replace("россия", "")
    t = t.replace("к.", "").replace("к-й.", "").replace("края", "").replace("в крае", "").replace("край", "")
    t =t.replace("оуфмс","отделуфмс")
    t =t.replace("отделениеуфмс","отделуфмс")
    t =t.replace("оуфмср","оуфмсроссии")
    t =t.replace("ао","автономныйокруг")
    t =t.replace("адм-й окр.", "административныйокруг")
    t =t.replace("ао", "автономнаяобласть")
    t =t.replace("авт.обл.", "автономнаяобласть")
    t =t.replace("пс", "паспортныйстол")
    t =t.replace("тп", "территориальныйпункт")
    t =t.replace("терпункт", "территориальныйпункт")
    t =t.replace("тер-й пункт", "территориальныйпункт")
    t =t.replace("овд", "отделвнутреннихдел")
    t =t.replace("мо", "межрайонныйотдел")
    t =t.replace("мро", "межрайонныйотдел")
    t =t.replace("мп", "миграционныйпункт")
    t =t.replace("говд", "городскойотделвнутреннихдел")
    t =t.replace("гу", "главноеуправление")
    t =t.replace("гор.ом", "городскойотделмилиции")
    t =t.replace("увд", "управлениевнутреннихдел")
    t =t.replace("мп", "миграционныйпункт")
    t = t.replace(".", "").replace(",", "").replace(" ", "").replace("-", "")
    return t 
st.set_page_config(
    page_title="Тренажёр фотоидентификации МФО",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Тренажёр фотоидентификации для МФО")

st.markdown("""
---
👋 **Добро пожаловать в тренажёр фотоидентификации!**  

-Это не просто тест, а полноценный симулятор реальных кейсов, с которыми ежедневно сталкиваются специалисты МФО при проверке документов клиентов.
""")

c1, c2 = st.columns([3, 1])
with c1:
    st.write("Прохождение теста займёт 10–20 минут вы проработаете 30 практических ситуаций: это поможет быстро выявить зоны роста и надёжно закрепить стандарты, принятые в компании.")
with c2:
    st.info("💡 В любой момент можно выйти — результаты сохранятся автоматически.")

st.divider()

st.header("Что важно знать перед стартом")

expander = st.expander("✅ Требования к сотруднику (чек-лист)", expanded=False)
expander.markdown("""
| Пункт | Описание |
| --- | --- |
| **Теория ФИ** | 1.1. Положение о паспорте РФ, 1.2. 2 страница паспорта, 1.3. 3 страница паспорта, 1.4. Лицо клиента(Селфи), 1.5. Данные подлежащие к проверке, 1.6. Причины отклонения фото, 1.7. Оценка подлинности паспорта гражданина РФ.|
| **Практика ФИ** | 2.1. Порядок проверки фото, 2.2. Особенности проверки фото по совокупности, 2.3. Редактирование данных в анкете, 2.4. Порядок внесения в ЧС.|
""")

st.warning("⚠️ **Обратите внимание:**  игнорирование любого из пунктов теории или практики фотоидентификации увеличивает риск ошибки при проверке документов. Это напрямую сказывается на скорости обработки заявки и может стать причиной пропуска мошеннических кейсов либо необоснованного отказа добросовестному клиенту.")

if 'cases_list' not in st.session_state:
    st.session_state.cases_list = []
if 'total_q' not in st.session_state:
    st.session_state.total_q = 0
if 'started' not in st.session_state:
    st.session_state.started = False
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'score' not in st.session_state:
    st.session_state.score = 0
if st.session_state.started == False:    
    full_name = st.text_input('Введите ваше ФИО для начала теста😊:')
    if st.button("«Начать обучение»😉:"):
        if full_name.strip() == '':
            st.warning('⚠️ Пожалуйста, сначала введите ФИО.')
        else:
            try:
                connection = psycopg2.connect(
                port = os.getenv('DB_PORT'),  
                host = os.getenv('DB_HOST'),  
                user = os.getenv('DB_USER'),
                password = os.getenv('DB_PASSWORD'),
                database = os.getenv('DB_DATABASE')
                )  
                cursor = connection.cursor()
                cursor.execute('SELECT case_id, description, correct_reason_id, check_type, last_name, frist_name, patronymic, gender, birth_date, passport_sn, issue_date, issued_by, dep_code, birth_place, draft_last_name, draft_frist_name, draft_patronymic, draft_gender, draft_birth_date, draft_passport_sn, draft_issue_date, draft_issued_by, draft_dep_code, draft_birth_place FROM "Trainer".exam_cases WHERE description IS NOT NULL ORDER BY RANDOM();')     
                cases = cursor.fetchall()
                st.session_state.cases_list = cases
                st.session_state.total_q = len(cases)
                st.session_state.started = True
                st.session_state.user_name = full_name
                cursor.close()
                connection.close()
                st.rerun()
            except Exception as error:
                print(f"Критическая ошибка: {error}")
                st.error("Извините, произошла техническая неполадка. Попробуйте перезагрузить страницу.")
else:
    st.write(f"👤 Сотрудник:**{st.session_state.user_name}**")
    if st.session_state.step > st.session_state.total_q and st.session_state.total_q > 0:
        st.balloons()
        st.title('🏆 Тест завершён 🏆')
        sum_pro = (st.session_state.score / st.session_state.total_q) * 100
        rand_procent = round(sum_pro,1)
        st.write(f"Твой результат: **{rand_procent}%** вопросов.")
        st.write(f"Успешно пройдено кейсов: **{ st.session_state.score}**")
        if st.button('Пройти заново 🔄'):
            st.session_state.started = False
            st.session_state.step = 1
            st.session_state.score = 0
            st.session_state.total_q = 0
            st.session_state.cases_list = []
            st.rerun()
    else:
        st.write(f"📊 Текущий шаг: **{st.session_state.step}**")
    try:
        connection = psycopg2.connect(
        port = os.getenv('DB_PORT'),  
        host = os.getenv('DB_HOST'),  
        user = os.getenv('DB_USER'),
        password = os.getenv('DB_PASSWORD'),
        database = os.getenv('DB_DATABASE')
        )       
        cursor = connection.cursor()
        current_case = st.session_state.cases_list[min(st.session_state.step,st.session_state.total_q) - 1]
        current_id = current_case[0]
        description = current_case[1]
        correct_answer = current_case[2]
        current_check_type = current_case[3]
        db_last_name = current_case[4]
        db_frist_name = current_case[5]
        db_patronymic = current_case[6]
        db_gender = current_case[7]
        db_birth_date = current_case[8]
        db_passport_sn = current_case[9]
        db_issue_date = current_case[10]
        db_issued_by = current_case[11]
        db_dep_code = current_case[12]
        db_birth_place = current_case[13]
        draft_last_name = current_case[14]
        draft_frist_name = current_case[15]
        draft_patronymic = current_case[16]
        draft_gender = current_case[17]
        draft_birth_date = current_case[18]
        draft_passport_sn = current_case[19]
        draft_issue_date = current_case[20]
        draft_issued_by = current_case[21]
        draft_dep_code = current_case[22]
        draft_birth_place = current_case[23]
        cursor.execute("""SELECT reason_name FROM "Trainer".reasons_directory WHERE (check_type = \'all\' OR check_type = %s) AND reason_id <> 0 ORDER BY reason_id ASC;""", (current_check_type,))
        row = cursor.fetchall()
        clean_reasons = [i[0] for i in row]
        col_photo,col_anketa = st.columns(2, vertical_alignment="center")
        with col_photo:
             st.subheader(f"КЕЙС № {current_id}")
             st.write(description)
             col_btn_left, col_btn_right = st.columns(2,vertical_alignment="center")
             with col_btn_left:
                 st.write('')
                 st.write('')
                 st.write('')
                 st.write('')
                 st.write('')
                 accept_button = st.button(label = 'Принять',use_container_width=True)
             with col_btn_right:
                 reject_button = st.button(label= 'Отправить ответ на проверку!✨')
                 user_choice = st.selectbox('Отклонить⬇️',clean_reasons)
             st.write('---')
             st.image(f"case{current_id}.jpg",use_container_width=True)
        with col_anketa:
            st.write('')
            st.write('')
            st.write('')
            st.write('')
            st.write('')
            st.write('')
            st.write('')
            st.write('')
            st.subheader('📝 Данные анкеты заявки')
            last_name = st.text_input("Фамилия:", value=draft_last_name)
            frist_name = st.text_input("Имя:", value=draft_frist_name)
            patronymic = st.text_input("Отчество:", value=draft_patronymic)
            gender = st.text_input("Пол:", value=draft_gender)
            birth_date = st.text_input("Дата рождения:", value=draft_birth_date)
            passport_sn = st.text_input("Сирия-Номер:", value=draft_passport_sn)
            issue_date = st.text_input("Дата выдачи:", value=draft_issue_date)
            issued_by = st.text_input("Выдан:", value=draft_issued_by)
            dep_code = st.text_input("Код подразделения:", value=draft_dep_code)
            birth_place = st.text_input("Место рождения:", value=draft_birth_place)
        if accept_button:
            user_number = '0'
            anketa_is_ok =(
                clean_text(last_name) == clean_text(db_last_name) and
                clean_text(frist_name) == clean_text(db_frist_name) and
                clean_text(patronymic) == clean_text(db_patronymic) and
                clean_text(gender) == clean_text(db_gender) and
                clean_text(birth_date) == clean_text(db_birth_date) and
                clean_text(passport_sn) == clean_text(db_passport_sn) and
                clean_text(issue_date) == clean_text(db_issue_date) and
                clean_text(issued_by) == clean_text(db_issued_by) and
                clean_text(dep_code) == clean_text(db_dep_code) and
                clean_text(birth_place) == clean_text(db_birth_place))
            if anketa_is_ok and int(str(correct_answer).strip()) == 0:
                st.success('Верно!✅')
                is_correct = 'True'
                st.session_state.score += 1
            else:
                st.error('Ошибка!⚠️')
                is_correct = 'False'
            sql_insert ="""INSERT INTO "Trainer".learning_logs(full_name,cases_id,answer_name,result_answer)
                            VALUES(%s,%s,%s,%s);"""
            cursor.execute(sql_insert,(st.session_state.user_name,current_id,user_number,is_correct))
            connection.commit()
            st.session_state.step += 1
            st.rerun()
        if reject_button:
            user_number = user_choice.split('.')[0].strip()
            if int(user_number) == int(str(correct_answer).strip()):
                st.success('Верно!✅')
                is_correct = 'True'
                st.session_state.score += 1
            else:
                st.error('Ошибка!⚠️')
                is_correct = 'False'
            sql_insert ="""INSERT INTO "Trainer".learning_logs(full_name,cases_id,answer_name,result_answer)
                             VALUES (%s,%s,%s,%s);"""
            cursor.execute(sql_insert,(st.session_state.user_name,current_id,user_number,is_correct))
            connection.commit()
            st.session_state.step += 1
            st.rerun()
            
    except Exception as error:
            print(f"Критическая ошибка: {error}")
            st.error("Извините, произошла техническая неполадка. Попробуйте перезагрузить страницу.")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
    if st.button('Выйти из тренажёра❌'):
        st.session_state.started = False
        st.session_state.step = 1
        st.session_state.score = 0
        st.session_state.total_q = 0
        st.session_state.cases_list = []
        st.rerun()    
