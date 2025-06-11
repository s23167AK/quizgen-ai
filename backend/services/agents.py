from io import BytesIO
from typing import Annotated, Literal
from typing_extensions import TypedDict, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from PIL import Image

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


load_dotenv()

llm = init_chat_model(
    "openai:gpt-4o"
)



class Question(BaseModel):
    question_type: Literal[
        'short_answer',
        'multiple_choice',
        'fill_in_blank',
    ] = Field(
        ...,
        description='Rodzaj pytania. Opcje do wybrania: short_answer, multiple_choice, fill_in_blank'
    )
    question: str = Field(..., description='Pytanie do podanych notatek')
    options: str | None = Field(
        description='Opcjonalne pole, używane tylko w przypadku użycia podanych rodzajów pytań: multiple_choice question_type. Wypisz odpowiedzi w liście alfabetycznej.')
    correct_answer: str = Field(..., description='Prawidłowa odpowiedź na pytanie')


class Quiz(BaseModel):
    questions: List[Question]


class QuestionResult(BaseModel):
    question_result: Literal[
        'Correct',
        'InCorrect',
        'PartiallyCorrect'
    ] = Field(
        ...,
        description='Wynik odpowiedzi na pytanie. Dostępne opcje: Correct, InCorrect, PartiallyCorrect'
    )


class State(TypedDict):
    messages: Annotated[list, add_messages]
    note_content: str
    number_of_questions: int
    quiz: Quiz
    question_index: int
    question_result: QuestionResult | None
    ready_to_finish: bool
    user_answer: str
    correct_answer_count: int
    partially_correct_answer_count: int
    incorrect_answer_count: int
    allow_short_answer: bool
    allow_multiple_choice: bool
    allow_fill_in_blank: bool


def quizgen(state: State):
    quizgen_llm = llm.with_structured_output(Quiz)
    question_count = state['number_of_questions']
    note_content = state.get('note_content')
    allow_short_answer = state.get('allow_short_answer')
    allow_multiple_choice = state.get('allow_multiple_choice')
    allow_fill_in_blank = state.get('allow_fill_in_blank')

    prompt = (
        f"Na podstawie poniższej notatki wygeneruj quiz w języku polskim.\n"
        f"Wygeneruj jedynie zadania o typie"
        f"Liczba pytań: {question_count}.\n"
        f"NOTATKA:\n{note_content}\n\n"
        f"Masz dostępnych kilka opcji pytań. Możesz użyć jedynie opcji z flagą: YES"
        f"short_answer " + "YES" if allow_short_answer else "NO"
        f"multiple_choice " + "YES" if allow_multiple_choice else "NO"
        f"fill_in_blank " + "YES" if allow_fill_in_blank else "NO"
    )

    result = quizgen_llm.invoke([
        {
            'role': 'system',
            'content': prompt
        }
    ])

    return {'quiz': result}


def next_question(state: State):
    quiz = state.get('quiz')
    question_index = state.get('question_index')
    question_index += 1
    if question_index >= len(quiz.questions):
        return {'ready_to_finish': True}
    question = quiz.questions[question_index]
    print(bcolors.YELLOW + 'Correct answer: --->', question.correct_answer + bcolors.ENDC)
    return {'ready_to_finish': False, 'question_index': question_index,
            'messages': [{'role': 'assistant', 'content': question.question}]}


def human(state: State):
    quiz = state.get('quiz')
    question_index = state.get('question_index')
    question = quiz.questions[question_index]
    result = interrupt(
        {
            "question": question
        }
    )

    return {'messages': [{'role': 'user', 'content': result['answer']}], 'user_answer': result['answer']}


def validator_agent(state: State):
    validation_llm = llm.with_structured_output(QuestionResult)

    quiz = state.get('quiz')
    question_index = state.get('question_index')

    question = quiz.questions[question_index]
    user_answer = state.get('user_answer')

    prompt = (
        f"Oceń odpowiedź użytkownika na pytanie quizowe. "
        f"Twoim zadaniem jest sprawdzić, czy odpowiedź użytkownika jest poprawna, nawet jeśli użyto innych słów, pojawiły się literówki lub synonimy. "
        f"Oceń bardzo łagodnie, jeśli znaczenie jest tożsame, bardzo bliskie lub tylko trochę niepełne, uznaj odpowiedź za poprawną.\n"
        f"\n"
        f"Pytanie: {question.question}\n"
        f"Poprawne odpowiedzi (przynajmniej jedna): {question.correct_answer}\n"
        f"Odpowiedź użytkownika: {user_answer}\n"
        # f"Odpowiedz tylko jednym słowem: True jeśli poprawne, False jeśli błędne."
    )
    result = validation_llm.invoke([
        {
            'role': 'system',
            'content': prompt
        }
    ])
    correct_answer_count = state['correct_answer_count']
    incorrect_answer_count = state['incorrect_answer_count']
    partially_correct_answer_count = state['partially_correct_answer_count']

    print(result.question_result)
    
    match (result.question_result):
        case 'Correct':
            correct_answer_count += 1
        case 'InCorrect':
            incorrect_answer_count += 1
        case 'PartiallyCorrect':
            partially_correct_answer_count += 1

    return {
        'question_result': result,
        'messages': [{'role': 'assistant', 'content': result.question_result}],
        'correct_answer_count': correct_answer_count,
        'incorrect_answer_count': incorrect_answer_count,
        'partially_correct_answer_count': partially_correct_answer_count,
    }


def additional_question_agent(state: State):
    print('additional_question_agent')
    additional_question_llm = llm.with_structured_output(Question)

    note_content = state.get('note_content')

    quiz = state.get('quiz')
    question_index = state.get('question_index')

    question = quiz.questions[question_index]
    user_answer = state.get('user_answer')

    prompt = (
        f"Sprawdź dokładnie odpowiedź użytkownika, porównaj ją z poprawną odpowiedzią to zadanego pytania, "
        f"które zostało stworzone na podstawie poniższej notatki, nie zdradzaj użytkownikowi poprawnej odpowiedzi."
        f"Wygeneruj pytanie naprowadzające użytkownika, dopytujące się o treść zadanego pytania."
        f"Notatka: {note_content}\n"
        f"Pytanie: {question.question}\n"
        f"Poprawne odpowiedzi (przynajmniej jedna): {question.correct_answer}\n"
        f"Odpowiedź użytkownika: {user_answer}\n"
        # f"Odpowiedz tylko jednym słowem: True jeśli poprawne, False jeśli błędne."
    )
    result = additional_question_llm.invoke([
        {
            'role': 'system',
            'content': prompt
        }
    ])

    quiz = state['quiz']

    quiz.questions.insert(question_index + 1, result)

    return {'quiz': quiz}


def explanation_agent(state: State):
    print('explanation_agent')
    question_index = state['question_index']
    question = state['quiz'].questions[question_index]
    user_answer = state.get('user_answer')
    note_content = state['note_content']
    prompt = (
        "Wyjaśnij dlaczego moja odpowiedź jest nieprawidłowa.\n\n"
        f"Pytanie: {question.question}\n"
        f"Moja odpowiedź: {user_answer}\n"
        f"Poprawna odpowiedź: {question.correct_answer}\n"
        f"Notatka: {note_content}\n"
    )
    response = llm.invoke([{
        'role': 'user',
        'content': prompt
    }])
    print(response.content)
    return {'messages': [{'role': 'user', 'content': response.content}]}


def summary_agent(state: State):
    prompt = (
        "Podsumuj odpowiedzi użytkownika w formacie:"
        "Podsumowanie odpowiedzi"
        f"Ilość poprawnych odpowiedzi: {state['correct_answer_count']}"
        f"Ilość częściowo poprawnych odpowiedzi: {state['partially_correct_answer_count']}"
        f"Ilość błędnych odpowiedzi: {state['incorrect_answer_count']}"
        "Wypisz mu na podstawie głównie błędnych odpowiedzi,"
        " może odrobine z częściowo poprawnych co powinien powtórzyć z materiału.\n"
        f"Messages: {state['messages']}"
    )
    response = llm.invoke([{
        'role': 'system',
        'content': prompt
    }])
    print(response.content)
    return {'messages': [{'role': 'user', 'content': response.content}]}


def get_question_result(state: State):
    question_result = state.get('question_result')
    if question_result:
        return question_result.question_result
    else:
        raise ValueError


graph_builder = StateGraph(State)

graph_builder.add_node('quizgen', quizgen)
graph_builder.add_node('next_question', next_question)
graph_builder.add_node('human', human)
graph_builder.add_node('validator_agent', validator_agent)
graph_builder.add_node('additional_question_agent', additional_question_agent)
graph_builder.add_node('explanation_agent', explanation_agent)
graph_builder.add_node('summary_agent', summary_agent)

graph_builder.add_edge(START, 'quizgen')
graph_builder.add_edge('quizgen', 'next_question')
graph_builder.add_conditional_edges(
    'next_question',
    lambda state: state.get("ready_to_finish", False),
    {True: 'summary_agent', False: "human"}
)
graph_builder.add_edge('human', 'validator_agent')
graph_builder.add_conditional_edges(
    'validator_agent',
    lambda state: get_question_result(state),
    {"Correct": "next_question", "InCorrect": "explanation_agent", "PartiallyCorrect": "additional_question_agent"}
)
graph_builder.add_edge('explanation_agent', 'next_question')
graph_builder.add_edge('additional_question_agent', 'next_question')
graph_builder.add_edge('summary_agent', END)

checkpointer = MemorySaver()

graph = graph_builder.compile(checkpointer=checkpointer)


def show_graph(g):
    image_data = graph.get_graph().draw_mermaid_png()
    # image_data = dot.pipe(format='png')

    # Load image using Pillow
    image = Image.open(BytesIO(image_data))
    image.show()


def validate_state(state):
    '''
    Validates current graph state.

    :param state: Current graph state.
    :return: Returns None if quiz has ended or Question object for user.
    '''
    try:
        return state.tasks[0].interrupts[0].value['question']
    except:
        return


def run_chatbot(note_content: str,
                number_of_questions: int,
                thread_id: str,
                allow_short_answer=True,
                allow_multiple_choice=True,
                allow_fill_in_blank=True,
                debug=False):
    '''
    Creates graph with given thread_id.

    :param note_content: Note that will be used to generate quiz.
    :param thread_id: Name of a thread.
    :param debug: Optional parameter to show chatbot logs. Default is False.
    :return: Returns None if quiz has ended or quiz question for user.
    '''
    thread_config = {"configurable": {"thread_id": thread_id}}
    state = {
        'messages': [],
        'note_content': note_content,
        'number_of_questions': number_of_questions,
        'questions': [],
        'question_index': -1,
        'question_result': None,
        'ready_to_finish': False,
        'correct_answer_count': 0,
        'incorrect_answer_count': 0,
        'partially_correct_answer_count': 0,
        'allow_short_answer': allow_short_answer,
        'allow_multiple_choice': allow_multiple_choice,
        'allow_fill_in_blank': allow_fill_in_blank,
    }
    graph.invoke(state, debug=debug, config=thread_config)

    state = graph.get_state(thread_config)

    return validate_state(state)


def continue_chatbot(thread_id: str, user_answer: str, debug=False):
    '''
    Continues graph with given id. Uses user_answer param to continue the quiz.

    :param thread_id: Name of a thread.
    :param user_answer: User's answer to quiz question.
    :param debug: Optional parameter to show chatbot logs. Default is False.
    :return: Returns None if quiz has ended or quiz question for user.
    '''
    thread_config = {"configurable": {"thread_id": thread_id}}
    graph.invoke(
        Command(resume={'answer': user_answer}),
        config=thread_config,
        debug=debug
    )

    state = graph.get_state(thread_config)

    return validate_state(state)


if __name__ == '__main__':  # Use for testing
    note = ('Fotosynteza to proces zachodzący w roślinach zielonych,'
            ' podczas którego energia świetlna przekształcana jest w energię chemiczną. '
            'Rośliny pobierają dwutlenek węgla z powietrza i wodę z gleby,'
            ' a dzięki obecności chlorofilu oraz światła słonecznego produkują tlen i glukozę.'
            'Fotosynteza jest podstawą życia na Ziemi – dostarcza tlenu i stanowi źródło pożywienia dla organizmów '
            'żywych.')
    thread_id = 'test'
    debug = True
    number_of_questions = 10
    result = run_chatbot(note, number_of_questions, thread_id, allow_multiple_choice=False, debug=debug)
    while True:
        if not result:
            break

        print('====================')
        if result.options: print(result.options)
        user_answer = input(bcolors.RED + result.question + bcolors.ENDC).strip()

        result = continue_chatbot(thread_id, user_answer=user_answer, debug=debug)
