class Detail:
    def __init__(self, name, state=None):
        self.__name = name
        self.__development = {}
        self.__ready = False
        self.set_state(state)

    @property
    def name(self):
        return self.__name

    @property
    def ready(self):
        return self.__ready

    def set_state(self, state: dict):
        """
        добавляет документы в разработку; если документ существует, сохраняет обновленное состояние документа
        типы: detail[doc_name:str] = doc_state:bool
        """
        if state is None:
            return
        if self.__ready:
            print('|E|detail is already developed')
            return
        if not isinstance(state, dict):
            print('|E|state is not dict')
            return
        for key, value in state.items():
            state[key] = bool(value)
            if not isinstance(key, str):
                print('|E|name of document is not str')
                state.pop(key, None)
        self.__development.update(state)

    def get_state(self):
        """возвращает словарь документов и их значений"""
        return self.__development

    def delete_document(self, name):
        """Удаляет документ по имени"""
        self.__development.pop(name, None)

    def check_preparedness(self):
        """True если все документы готовы или документов нет"""
        return all(self.__development.values())

    def process(self):
        """отправка разработки на производство"""
        if self.check_preparedness():
            self.__ready = True

    def unprocess(self):
        """Возвращение детали из производства"""
        self.__ready = False
