import wx
from FileWorker import File
from Detail import Detail


class Frame(wx.Frame):
    def __init__(self):
        super().__init__(None,
                         title='Система контроля конструкторской документации',
                         size=(600, 400),
                         id=wx.ID_ANY,
                         style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.SetIcon(wx.Icon('Icon8.ico'))
        self.Centre()
        self.detail_selection = None
        self.__doc_selection = None
        self.saved = True
        self.__password = '12345'
        self.__details = []
        prev_save_file = File('bin/savefile_1.save').download()  # Поиск сохранений

        if not isinstance(prev_save_file, str) or prev_save_file == '':
            self.__file = File()
        else:
            self.__file = File(prev_save_file)
            save = self.__file.download()

            if save is None:
                File('bin/savefile_1.save').upload('saves/Details.dev')
            elif save:
                answ = wx.MessageBox(
                    caption='Система контроля конструкторской документации',
                    message='Загрузить предыдущее сохранение?',
                    style=wx.YES_NO | wx.CENTRE | wx.ICON_NONE,
                    parent=self
                )
                self.__details = save if answ == wx.YES else []

        psw = File('bin/savefile_2.save').download()
        if psw:
            self.__password = psw
        self.__developed_details = []
        other = []  # разделение деталей на разработанные и нет
        for i, x in enumerate(self.__details):
            if x.ready:
                self.__developed_details.append(x)
            else:
                other.append(x)
        self.__details = other
        self.Klim_counter = 0
        panel = wx.Panel(self, id=wx.ID_ANY, pos=(0, 10), size=(600, 390))  # размещение элементов интерфейса
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        docs_statbox = wx.StaticBox(panel,
                                    label='Документы:',
                                    id=wx.ID_ANY,
                                    pos=(0, 0),
                                    size=(225, 80))
        hbox.Add(docs_statbox, flag=wx.RIGHT, border=10)
        self.__docs_combox = wx.ComboBox(docs_statbox,
                                         id=wx.ID_ANY,
                                         pos=(15, 22),
                                         size=(197, 25),
                                         style=wx.CB_READONLY,
                                         choices=[])
        self.Bind(wx.EVT_COMBOBOX, self.__docs_combox_click, id=self.__docs_combox.GetId())
        self.__tick = wx.CheckBox(docs_statbox,
                                  id=wx.ID_ANY,
                                  label='Подтвердить наличие документа',
                                  pos=(15, 55))
        self.Bind(wx.EVT_CHECKBOX, self.__doc_tick_click, id=self.__tick.GetId())
        details_statbox = wx.StaticBox(panel,
                                       label='Разработка:',
                                       id=wx.ID_ANY,
                                       pos=(0, 0),
                                       size=(225, 80))
        hbox.Add(details_statbox, flag=wx.LEFT, border=10)
        self.__details_combox = wx.ComboBox(details_statbox,
                                            id=wx.ID_ANY,
                                            pos=(15, 22),
                                            size=(197, 25),
                                            style=wx.CB_READONLY,
                                            choices=[])
        self.Bind(wx.EVT_COMBOBOX, self.__detail_combox_click, id=self.__details_combox.GetId())
        self.__progress_bar = wx.Gauge(details_statbox,
                                       id=wx.ID_ANY,
                                       range=100,
                                       pos=(15, 55),
                                       size=(197, 15),
                                       style=wx.GA_HORIZONTAL | wx.GA_SMOOTH)
        self.__ready_button = wx.Button(panel,
                                        label='Подтвердить\nготовность\nпельменей',
                                        id=wx.ID_ANY,
                                        pos=(0, 0),
                                        size=(130, 55),
                                        style=wx.NO_BORDER)
        vbox.Add(hbox, flag=wx.TOP | wx.CENTRE, border=80)
        vbox.Add(self.__ready_button, flag=wx.TOP | wx.BOTTOM | wx.CENTRE, border=30)
        panel.SetSizer(vbox)
        self.Bind(wx.EVT_BUTTON, self.__ready_button_click, id=self.__ready_button.GetId())
        menu_bar = wx.MenuBar()  # Меню
        self.SetMenuBar(menu_bar)
        file_menu = wx.Menu()
        menu_bar.Append(file_menu, 'Файл')
        menu_open = file_menu.Append(wx.ID_ANY, 'Открыть')
        self.Bind(wx.EVT_MENU, self.__open, menu_open)
        menu_save = file_menu.Append(wx.ID_ANY, 'Сохранить')
        self.Bind(wx.EVT_MENU, self.__save, menu_save)
        menu_save_as = file_menu.Append(wx.ID_ANY, 'Сохранить как')
        self.Bind(wx.EVT_MENU, self.__save_button_click, menu_save_as)
        menu_exit = file_menu.Append(wx.ID_ANY, 'Выйти')
        self.Bind(wx.EVT_MENU, self.__exit, menu_exit)
        find_menu = wx.Menu()
        menu_bar.Append(find_menu, 'Поиск')
        menu_find_detail = find_menu.Append(wx.ID_ANY, 'Поиск разработки')
        self.Bind(wx.EVT_MENU, self.__find_detail, menu_find_detail)
        menu_find_doc = find_menu.Append(wx.ID_ANY, 'Поиск документа')
        self.Bind(wx.EVT_MENU, self.__find_doc, menu_find_doc)
        self.__admin_menu = wx.Menu()
        menu_bar.Append(self.__admin_menu, 'Администрирование')
        self.__menu_login = self.__admin_menu.Append(wx.ID_ANY, 'Войти')
        self.Bind(wx.EVT_MENU, self.__log_in, self.__menu_login)
        self.SetAcceleratorTable(wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('S'), menu_save.GetId())]))
        self.Bind(wx.EVT_CLOSE, self.__exit)
        # установка начального положения и запуск окон
        self.doc_frame = DocFrame(self, self.__details, self.__developed_details)
        self.det_frame = DetFrame(self, self.__details, self.__developed_details)
        self.admin_frame = AdminFrame(self, self.__details, self.__developed_details)
        self.set_details_combox()
        self.set_docs_combox()
        self.__update_progress_bar()
        self.Show()

    def __detail_combox_click(self, event):
        """действия при выборе какой-либо детали"""
        self.Klim_counter = 0
        choice = self.__details_combox.GetSelection()
        if choice < len(self.__details):
            self.detail_selection = choice
            self.set_docs_combox()
            self.__update_progress_bar()
        else:
            if self.detail_selection and self.__details_combox.GetCount() > 1:
                self.__details_combox.SetSelection(self.detail_selection)
            else:
                self.__docs_combox.SetSelection(wx.NOT_FOUND)
            self.__create_detail()

    def __docs_combox_click(self, event):
        """действия при выборе какого-либо документа"""
        self.Klim_counter = 0
        choice = event.GetEventObject().GetSelection()
        if choice < self.__docs_combox.GetCount() - 1:
            self.__set_tick_value()
            self.__doc_selection = choice
        else:
            if self.__doc_selection and self.__docs_combox.GetCount() > 1:
                self.__docs_combox.SetSelection(self.__doc_selection)
            else:
                self.__docs_combox.SetSelection(wx.NOT_FOUND)
            self.__create_doc()

    def __doc_tick_click(self, event):
        """действия при нажатии галочки в главном окне"""
        self.Klim_counter = 0
        doc = self.__docs_combox.GetStringSelection()
        value = event.GetEventObject().GetValue()
        self.saved = False
        for detail in self.__details:
            if doc in detail.get_state().keys():
                detail.set_state({doc: value})
        self.__update_progress_bar()

    def __ready_button_click(self, event):
        """действия при нажатии кнопки отправки детали в производство"""
        if self.__details:
            if not self.__details[self.__details_combox.GetSelection()].check_preparedness():
                if self.Klim_counter == 2:
                    wx.MessageBox(caption=' ',
                                  message='Привет, Клим!',
                                  style=wx.OK | wx.CENTRE,
                                  parent=self)
                    self.Klim_counter = 0
                else:
                    wx.MessageBox(caption='Ошибка',
                                  message='Ещё не все документы готовы',
                                  style=wx.OK | wx.CENTRE | wx.ICON_WARNING,
                                  parent=self)
                    self.Klim_counter += 1
                return
            self.__delete_detail()
            wx.MessageBox(caption='Готово!',
                          message='Деталь переведена в статус производства',
                          style=wx.OK | wx.CENTRE | wx.ICON_INFORMATION)
            self.Klim_counter = 0
        else:
            wx.MessageBox(caption='Ошибка',
                          message='Нет деталей в разработке',
                          style=wx.OK | wx.CENTRE | wx.ICON_WARNING,
                          parent=self)

    def __create_detail(self, event=None):
        """Открытие окна создания новой разработки"""
        self.Klim_counter = 0
        self.Hide()
        self.det_frame.Show()

    def __create_doc(self, event=None):
        """Открытие окна создания нового документа"""
        if self.__details:
            self.doc_frame.update_combox([x.name for x in self.__details])
            self.doc_frame.update_text()
            self.doc_frame.update_text_all()
            self.Hide()
            self.doc_frame.Show()
        else:
            wx.MessageBox(caption='Извиняюсь',
                          message='Для добавления документов сначала нужно добавить разработки',
                          style=wx.OK_DEFAULT | wx.CENTRE | wx.ICON_WARNING,
                          parent=self)

    def __show_details(self, event=None):
        """Просмотр списка всех разработок и документов"""
        self.Klim_counter = 0
        self.admin_frame.items_list_update()
        self.Hide()
        self.admin_frame.Show()

    def __find_detail(self, event=None):
        """Действия при нажатии кнопки поиска детали"""
        with wx.TextEntryDialog(parent=self,
                                caption='Поиск разработки',
                                message='Введите название:',
                                style=wx.OK | wx.CANCEL | wx.CENTRE) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return
            det_name = dialog.GetValue()
            if det_name in [x.name for x in self.__details]:
                self.detail_selection = [x.name for x in self.__details].index(det_name)
                self.__details_combox.SetSelection(self.detail_selection)
                self.set_docs_combox()
                self.__update_progress_bar()
            elif det_name in [x.name for x in self.__developed_details]:
                wx.MessageBox(caption=' ',
                              message=f'{det_name} уже разработана',
                              style=wx.OK | wx.CENTRE | wx.ICON_NONE,
                              parent=self)
            else:
                wx.MessageBox(caption='Ошибка',
                              message='Разработка не найдена',
                              style=wx.OK | wx.CENTRE | wx.ICON_WARNING,
                              parent=self)

    def __find_doc(self, event=None):
        """Действия при нажатии кнопки поиска документа"""
        if self.__details_combox.GetStringSelection() == '':
            wx.MessageBox(caption='Ошибка',
                          message='Разработка не выбрана',
                          style=wx.OK | wx.CENTRE | wx.ICON_WARNING,
                          parent=self)
            return
        with wx.TextEntryDialog(parent=self,
                                caption='Поиск документа',
                                message='Введите название:',
                                style=wx.OK | wx.CANCEL | wx.CENTRE) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return
            doc_name = dialog.GetValue()
            if doc_name in self.__details[self.__details_combox.GetSelection()].get_state().keys():
                self.__docs_combox.SetValue(doc_name)
                self.__doc_selection = self.__docs_combox.GetSelection()
                self.__set_tick_value()
            else:
                wx.MessageBox(caption='Ошибка',
                              message='Документ не найден',
                              style=wx.OK | wx.CENTRE | wx.ICON_WARNING,
                              parent=self)

    def __open(self, event=None):
        """Выбор файла сохранения и обновление списока разработок"""
        self.Klim_counter = 0
        with wx.FileDialog(self, 'Открыть файл', wildcard='Разработки (*.dev)|*.dev',
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return
            new_file = File(file_dialog.GetPath())
            if new_file.way == self.__file.way:
                return
            if not self.saved:
                answ = wx.MessageBox(caption=' ',
                                     message='Сохранить изменения в предыдущем файле?',
                                     style=wx.YES_NO | wx.CANCEL | wx.CENTRE | wx.ICON_WARNING,
                                     parent=self)
                if answ == wx.CANCEL:
                    return
                if answ == wx.YES:
                    self.__save()
            self.__file = new_file
            File('bin/savefile_1.save').upload(self.__file.way)
            save = self.__file.download()
            if save is None:
                print(f'|E| loading went wrong {self.__file.way=}')
                return
            self.__details.clear()
            self.__developed_details.clear()
            for i, x in enumerate(save):
                if x.ready:
                    self.__developed_details.append(x)
                else:
                    self.__details.append(x)
            self.set_details_combox()
            self.set_docs_combox()

    def __save_button_click(self, event=None):
        """Действия при нажатии кнопки сохранить как"""
        self.Klim_counter = 0
        with wx.FileDialog(self, 'Сохранить как', wildcard='Разработки (*.dev)|*.dev',
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return
            self.__file = File(file_dialog.GetPath())
            self.__save()

    def __log_in(self, event=None):
        """Открытие окна авторизации"""
        self.Klim_counter = 0
        with wx.TextEntryDialog(parent=self,
                                caption='Вход',
                                message='Введите пароль:',
                                value='12345',
                                style=wx.OK | wx.CANCEL | wx.CENTRE | wx.TE_PASSWORD) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return
            if dialog.GetValue() == self.__password:
                self.__admin_menu.Delete(self.__menu_login)
                menu_change = self.__admin_menu.Append(wx.ID_ANY, 'Сменить пароль')
                self.Bind(wx.EVT_MENU, self.__change_psw, menu_change)
                menu_details = self.__admin_menu.Append(wx.ID_ANY, 'Обзор разработок')
                self.Bind(wx.EVT_MENU, self.__show_details, menu_details)
            else:
                wx.MessageBox(caption='Ошибка',
                              message='Пароль неверный',
                              style=wx.OK_DEFAULT | wx.CENTRE | wx.ICON_WARNING,
                              parent=self)

    def __change_psw(self, event=None):
        """Изменение пароля для входа"""
        with wx.TextEntryDialog(parent=self,
                                caption='Смена пароля',
                                message='Введите новый пароль:',
                                value='',
                                style=wx.OK | wx.CANCEL | wx.CENTRE) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return
            new_psw = dialog.GetValue().strip()
            if len(new_psw) < 3:
                wx.MessageBox(caption='Ошибка',
                              message='Пароль слишком короткий',
                              style=wx.OK | wx.CENTRE | wx.ICON_WARNING,
                              parent=self)
            elif new_psw == self.__password:
                wx.MessageBox(caption='Ошибка',
                              message='Нельзя изменить пароль на существующий',
                              style=wx.OK | wx.CENTRE | wx.ICON_WARNING,
                              parent=self)
            else:
                self.__password = new_psw
                File('bin/savefile_2.save').upload(self.__password)
                wx.MessageBox(caption=' ',
                              message='Пароль изменён',
                              style=wx.OK | wx.CENTRE | wx.ICON_INFORMATION,
                              parent=self)

    def set_details_combox(self):
        """обновление списка разработок"""
        prev_name = self.__details_combox.GetStringSelection()
        while self.__details_combox.GetCount():  # очистка списка
            self.__details_combox.Delete(0)
        if self.__details:
            names = [x.name for x in self.__details]
            self.__details_combox.Insert(names, self.__details_combox.GetCount())
            self.detail_selection = names.index(prev_name) if prev_name and prev_name in names else 0
            self.__details_combox.SetSelection(self.detail_selection)
            self.__update_progress_bar()
        self.__details_combox.Insert('Добавить новую разработку', self.__details_combox.GetCount())

    def set_docs_combox(self):
        """обновление списка документов"""
        prev_name = self.__docs_combox.GetStringSelection()
        while self.__docs_combox.GetCount():  # очистка списка
            self.__docs_combox.Delete(0)
        if self.__details:
            state = list(self.__details[self.__details_combox.GetSelection()].get_state().keys())
            if state:  # вставка новых имен
                self.__docs_combox.Insert(state, self.__docs_combox.GetCount())
                if prev_name and prev_name in state:
                    self.__docs_combox.SetValue(prev_name)
                else:
                    self.__docs_combox.SetSelection(0)
                self.__doc_selection = self.__docs_combox.GetSelection()
        self.__docs_combox.Insert('Добавить новый документ', self.__docs_combox.GetCount())
        self.__set_tick_value()
        self.__update_progress_bar()

    def __set_tick_value(self):
        """установка значения галочки в главном окне"""
        if self.__details:
            state = self.__details[self.__details_combox.GetSelection()].get_state()
            if state and self.__docs_combox.GetStringSelection():
                self.__tick.SetValue(state[self.__docs_combox.GetStringSelection()])
            else:
                self.__tick.SetValue(False)
        else:
            self.__tick.SetValue(False)

    def __update_progress_bar(self):
        """обновление шкалы прогресса"""
        if self.__details:
            state = self.__details[self.__details_combox.GetSelection()].get_state()
            if state:
                n, m = 0, 0
                for i in state.values():
                    n += 1
                    if i:
                        m += 1
                self.__progress_bar.SetValue(int(m / n * 100))
            else:
                self.__progress_bar.SetValue(100)
        else:
            self.__progress_bar.SetValue(0)

    def __delete_detail(self):
        """перевод детали в производство"""
        number = self.__details_combox.GetSelection()
        detail = self.__details[number]
        detail.process()
        self.__developed_details.append(self.__details.pop(number))
        self.__details_combox.Delete(number)
        self.saved = False
        if self.__details:
            self.__details_combox.SetSelection(0)
            self.detail_selection = 0
        self.set_docs_combox()
        self.__update_progress_bar()

    def __exit(self, event=None):
        """выход из приложения"""
        answer = wx.MessageBox(caption='Выход',
                               message='Вы действительно хотите выйти?' if self.saved else
                               'Вы действительно хотите выйти?\nНесохранённые изменения будут удалены.',
                               style=wx.YES_NO | wx.CENTRE | (wx.ICON_NONE if self.saved else wx.ICON_WARNING),
                               parent=self)
        if answer == wx.YES:
            self.doc_frame.Destroy()
            self.det_frame.Destroy()
            self.Destroy()

    def __save(self, event=None):
        """сохранение разработок в файл"""
        if not self.__file:
            self.__file = File()
        self.__file.upload([*self.__details, *self.__developed_details])
        self.saved = True
        File('bin/savefile_1.save').upload(self.__file.way)  # Сохранение в файл


class DetFrame(wx.Frame):
    def __init__(self, parent, details, developed):
        self.main_window = parent
        self.__details = details
        self.__developed_details = developed
        super().__init__(self.main_window,
                         title='Добавление новой разработки',
                         size=(350, 250),
                         id=wx.ID_ANY,
                         style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.SetIcon(wx.Icon('Icon8.ico'))
        self.Centre()
        panel = wx.Panel(self, id=wx.ID_ANY)
        static_text = wx.StaticText(panel,
                                    id=wx.ID_ANY,
                                    label='Название разработки:',
                                    pos=(100, 45))
        self.__input_text = wx.TextCtrl(panel,
                                        id=wx.ID_ANY,
                                        value="",
                                        pos=(90, 70),
                                        size=(150, 20),
                                        style=wx.TE_CENTRE | wx.TE_PROCESS_ENTER)
        self.__button_enter = wx.Button(panel,
                                        label='Добавить',
                                        id=wx.ID_ANY,
                                        pos=(90, 105),
                                        size=(70, 30),
                                        style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.__det_add, id=self.__button_enter.GetId())
        self.__button_cancel = wx.Button(panel,
                                         label='Отмена',
                                         id=wx.ID_ANY,
                                         pos=(170, 105),
                                         size=(70, 30),
                                         style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.__exit, id=self.__button_cancel.GetId())
        self.Bind(wx.EVT_CLOSE, self.__exit)
        self.Bind(wx.EVT_CHAR_HOOK, self.__key_processing)

    def __key_processing(self, event):
        """ожидание нажатия Enter"""
        if event.GetKeyCode() == 13:
            self.__det_add()
        else:
            event.Skip()

    def __det_add(self, event=None):
        """проверка и добавление разработки"""
        det_name = self.__input_text.GetValue()
        det_name = det_name.strip()
        while '  ' in det_name:
            det_name = det_name.replace('  ', ' ')
        if len(det_name) < 3:
            wx.MessageBox(caption='Ошибка',
                          message='Название разработки слишком короткое',
                          style=wx.OK | wx.CENTRE | wx.ICON_WARNING,
                          parent=self)
        else:
            for i in det_name:
                if (not (('a' <= i <= 'z') or ('A' <= i <= 'Z') or ('0' <= i <= '9') or ('а' <= i <= 'я') or
                         ('А' <= i <= 'Я') or i == '-' or i == ' ' or i == 'ё' or i == 'Ё')):
                    wx.MessageBox(caption='Ошибка',
                                  message='Некорректное название разработки',
                                  style=wx.OK | wx.CENTRE | wx.ICON_WARNING,
                                  parent=self)
                    break
            else:
                if det_name in [x.name for x in [*self.__details, *self.__developed_details]]:
                    wx.MessageBox(caption='Ошибка',
                                  message='Разработка с таким названием уже существует',
                                  style=wx.OK | wx.CENTRE | wx.ICON_WARNING,
                                  parent=self)
                else:
                    self.__details.append(Detail(det_name))
                    self.__input_text.Clear()
                    self.main_window.saved = False
                    wx.MessageBox(caption=' ',
                                  message='Разработка добавлена',
                                  style=wx.OK | wx.CENTRE | wx.ICON_INFORMATION,
                                  parent=self)
                    self.__exit()

    def __exit(self, event=None):
        self.HideWithEffect(wx.SHOW_EFFECT_BLEND, 100)
        self.main_window.set_details_combox()
        self.main_window.Show()


class DocFrame(wx.Frame):
    def __init__(self, parent, details, developed):
        self.main_window = parent
        self.__details = details
        self.__developed_details = developed
        self.__panel = 0
        super().__init__(self.main_window,
                         title='Добавление нового документа',
                         size=(500, 350),
                         id=wx.ID_ANY,
                         style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.SetIcon(wx.Icon('Icon8.ico'))
        self.Centre()
        main_panel = wx.Panel(self, id=wx.ID_ANY, pos=(0, 0), size=(500, 350))
        left_panel = wx.Panel(main_panel, id=wx.ID_ANY, pos=(50, 75), size=(150, 110))  # Панель для текстового поля
        self.__combox_panel = wx.Panel(main_panel, id=wx.ID_ANY, pos=(230, 30),
                                       size=(270, 320))  # Панель для одной разработки
        self.__all_panel = wx.Panel(main_panel, id=wx.ID_ANY, pos=(230, 30),
                                    size=(270, 320))  # Панель для всех разработок
        self.__all_panel.Hide()
        static_text = wx.StaticText(left_panel,
                                    id=wx.ID_ANY,
                                    label='Название документа:',
                                    pos=(15, 0))
        self.__input_text = wx.TextCtrl(left_panel,
                                        id=wx.ID_ANY,
                                        value="",
                                        pos=(0, 25),
                                        size=(150, 20),
                                        style=wx.TE_CENTRE | wx.TE_PROCESS_ENTER)
        self.__tick = wx.CheckBox(left_panel,
                                  id=wx.ID_ANY,
                                  label='Для всех разработок',
                                  pos=(8, 55))
        self.Bind(wx.EVT_CHECKBOX, self.__tick_click, id=self.__tick.GetId())
        self.__button_enter = wx.Button(left_panel,
                                        label='Добавить',
                                        id=wx.ID_ANY,
                                        pos=(0, 75),
                                        size=(70, 30),
                                        style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.__doc_add, id=self.__button_enter.GetId())
        self.__button_cancel = wx.Button(left_panel,
                                         label='Отмена',
                                         id=wx.ID_ANY,
                                         pos=(80, 75),
                                         size=(70, 30),
                                         style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.__exit, id=self.__button_cancel.GetId())
        static_text_2 = wx.StaticText(self.__combox_panel,
                                      id=wx.ID_ANY,
                                      label='Разработка:',
                                      pos=(0, 3))
        self.__combox = wx.ComboBox(self.__combox_panel,
                                    id=wx.ID_ANY,
                                    pos=(70, 0),
                                    size=(130, 25),
                                    style=wx.CB_READONLY,
                                    choices=[x.name for x in self.__details])
        self.Bind(wx.EVT_COMBOBOX, self.update_text, id=self.__combox.GetId())
        static_text_3 = wx.StaticText(self.__combox_panel,
                                      id=wx.ID_ANY,
                                      label='Документы:',
                                      pos=(0, 35))
        self.__text_single = wx.TextCtrl(self.__combox_panel,
                                         id=wx.ID_ANY,
                                         value='',
                                         pos=(8, 55),
                                         size=(200, 175),
                                         style=wx.TE_MULTILINE | wx.TE_READONLY)
        static_text_4 = wx.StaticText(self.__all_panel,
                                      id=wx.ID_ANY,
                                      label='Документы:',
                                      pos=(0, 0))
        self.__text_all = wx.TextCtrl(self.__all_panel,
                                      id=wx.ID_ANY,
                                      value='',
                                      pos=(8, 20),
                                      size=(200, 210),
                                      style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.Bind(wx.EVT_CLOSE, self.__exit)
        self.Bind(wx.EVT_CHAR_HOOK, self.__key_processing)

    def __key_processing(self, event):
        """ожидание нажатия Enter"""
        if event.GetKeyCode() == 13:
            self.__doc_add()
        else:
            event.Skip()

    def __tick_click(self, event):
        """Действия при нажатии галочки"""
        if self.__panel == 0:
            self.__all_panel.Show()
            self.__combox_panel.Hide()
            self.__panel = 1
        else:
            self.__combox_panel.Show()
            self.__all_panel.Hide()
            self.__panel = 0

    def update_text(self, event=None):
        """
        Вызывается при выборе какой-либо разработки
        Обновляет текстовое поле одной разработки
        """
        text = ''
        for doc in self.__details[self.__combox.GetSelection()].get_state().keys():
            text += doc + '\n'
        self.__text_single.SetValue(text[:-1] if text else 'Нет документов')

    def update_text_all(self):
        """Обновляет текстовое поле всех разработок"""
        text = ''
        for detail in self.__details:
            text += detail.name + '\n'
            for doc in detail.get_state().keys():
                text += '• ' + doc + '\n'
            if not detail.get_state().keys():
                text += '• Нет документов\n'
        self.__text_all.SetValue(text[:-1])

    def __doc_add(self, event=None):
        """проверка и добавление документа"""
        current_detail = self.__details[self.__combox.GetSelection()]
        doc_name = self.__input_text.GetValue().strip()
        while '  ' in doc_name:
            doc_name = doc_name.replace('  ', ' ')
        if len(doc_name) < 3:
            wx.MessageBox(caption='Ошибка',
                          message='Название документа слишком короткое',
                          style=wx.OK | wx.CENTRE | wx.ICON_WARNING,
                          parent=self)
        else:
            for i in doc_name:
                if (not (('a' <= i <= 'z') or ('A' <= i <= 'Z') or ('0' <= i <= '9') or ('а' <= i <= 'я') or
                         ('А' <= i <= 'Я') or i == '-' or i == ' ' or i == 'ё' or i == 'Ё')):
                    wx.MessageBox(caption='Ошибка',
                                  message='Некорректное название документа',
                                  style=wx.OK | wx.CENTRE | wx.ICON_WARNING,
                                  parent=self)
                    break
            else:
                if self.__tick.GetValue() == 1:
                    for detail in self.__details:
                        if doc_name in detail.get_state().keys():
                            wx.MessageBox(caption='Ошибка',
                                          message=f'Такой документ уже существует в разработке {detail.name}',
                                          style=wx.OK | wx.CENTRE | wx.ICON_WARNING,
                                          parent=self)
                            break
                    else:
                        for detail in self.__details:
                            detail.set_state({doc_name: False})
                        wx.MessageBox(caption=' ',
                                      message='Документ добавлен',
                                      style=wx.OK | wx.CENTRE | wx.ICON_INFORMATION,
                                      parent=self)
                        self.main_window.saved = False
                        self.update_text_all()
                        self.update_text()
                        self.__input_text.Clear()
                else:
                    if doc_name in current_detail.get_state().keys():
                        wx.MessageBox(caption='Ошибка',
                                      message='Такой документ уже существует',
                                      style=wx.OK | wx.CENTRE | wx.ICON_WARNING,
                                      parent=self)
                    else:
                        current_detail.set_state({doc_name: False})
                        self.__input_text.Clear()
                        wx.MessageBox(caption=' ',
                                      message='Документ добавлен',
                                      style=wx.OK | wx.CENTRE | wx.ICON_INFORMATION,
                                      parent=self)
                        self.main_window.saved = False
                        self.update_text()
                        self.update_text_all()

    def update_combox(self, names):
        """Обновляет список разработок в комбоксе"""
        while self.__combox.GetCount():  # очистка списка
            self.__combox.Delete(0)
        if names:
            self.__combox.Insert(names, self.__combox.GetCount())
            self.__combox.SetSelection(self.main_window.detail_selection)

    def __exit(self, event=None):
        self.HideWithEffect(wx.SHOW_EFFECT_BLEND, 300)
        self.main_window.set_docs_combox()
        self.main_window.Show()


class AdminFrame(wx.Frame):
    def __init__(self, parent, details, developed):
        self.main_window = parent
        self.__details = details
        self.__developed_details = developed
        super().__init__(self.main_window,
                         title='Обзор разработок',
                         size=(450, 380),
                         id=wx.ID_ANY,
                         style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.SetIcon(wx.Icon('Icon8.ico'))
        self.Centre()
        panel = wx.Panel(self, id=wx.ID_ANY)
        left_panel = wx.Panel(panel, id=wx.ID_ANY, pos=(10, 10), size=(180, 350))
        right_panel = wx.Panel(panel, id=wx.ID_ANY, pos=(180, 0), size=(270, 350))
        self.__radio_button_1 = wx.RadioButton(left_panel,
                                               id=wx.ID_ANY,
                                               label='Разработки',
                                               pos=(10, 10))
        wx.RadioButton(left_panel,
                       id=wx.ID_ANY,
                       label='Документы',
                       pos=(10, 30))
        self.Bind(wx.EVT_RADIOBUTTON, self.__radiobutton_click)
        self.__items_amount = wx.StaticText(left_panel,
                                            id=wx.ID_ANY,
                                            label='',
                                            pos=(10, 50))
        self.__items_list = wx.ListBox(left_panel,
                                       id=wx.ID_ANY,
                                       pos=(10, 70),
                                       size=(130, 150),
                                       choices=[],
                                       style=wx.LB_SINGLE | wx.LB_NEEDED_SB)
        self.Bind(wx.EVT_LISTBOX, self.__listbox_click, id=self.__items_list.GetId())
        self.__info = wx.TextCtrl(right_panel,
                                  id=wx.ID_ANY,
                                  value='',
                                  pos=(0, 30),
                                  size=(230, 80),
                                  style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.__static_text_info = wx.StaticText(right_panel,
                                                id=wx.ID_ANY,
                                                label='',
                                                pos=(0, 110))
        self.__items_info_list = wx.ListBox(right_panel,
                                            id=wx.ID_ANY,
                                            pos=(0, 130),
                                            size=(230, 100),
                                            choices=[],
                                            style=wx.LB_SINGLE | wx.LB_NEEDED_SB)
        self.__delete_button = wx.Button(left_panel,
                                         label='Удалить разработку',
                                         id=wx.ID_ANY,
                                         pos=(10, 230),
                                         size=(130, 30),
                                         style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.__delete_1, id=self.__delete_button.GetId())
        self.__preparedness_button = wx.ToggleButton(left_panel,
                                                     id=wx.ID_ANY,
                                                     label='Разработка не готова',
                                                     pos=(10, 270),
                                                     size=(130, 30))
        self.Bind(wx.EVT_TOGGLEBUTTON, self.__prepare_button_click, id=self.__preparedness_button.GetId())
        self.__delete_button_2 = wx.Button(right_panel,
                                           label='Удалить документ из требуемых\nдля этой разработки',
                                           id=wx.ID_ANY,
                                           pos=(0, 240),
                                           size=(230, 45),
                                           style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.__delete_2, id=self.__delete_button_2.GetId())
        self.Bind(wx.EVT_CLOSE, self.__exit)

    def __radiobutton_click(self, event=None):
        self.items_list_update()

    def __listbox_click(self, event=None):
        """Действия при выборе объекта"""
        name = self.__items_list.GetStringSelection()
        if name == '• В разработке:' or name == '• Разработаны:':
            self.__items_list.Deselect(self.__items_list.GetSelection())
            return
        if self.__radio_button_1.GetValue():
            for detail in [*self.__details, *self.__developed_details]:
                if detail.name == name:
                    self.update_text(detail)
                    self.__delete_button.SetLabel('Удалить разработку')
                    self.__preparedness_button.SetLabel(
                        'Разработка готова' if detail.ready else 'Разработка не готова')
                    self.__preparedness_button.SetValue(detail.ready)
                    return
        else:
            for detail in [*self.__details, *self.__developed_details]:
                for doc, value in detail.get_state().items():
                    if doc == name:
                        self.update_text((doc, value))
                        self.__delete_button.SetLabel('Удалить документ')
                        self.__preparedness_button.SetLabel(
                            'Документ готов' if value else 'Документ не готов')
                        self.__preparedness_button.SetValue(value)
                        return

    def __delete_1(self, event=None):
        """Удаление документа/разработки"""
        name = self.__items_list.GetStringSelection()
        if not name:
            return
        if self.__radio_button_1.GetValue():
            for i, detail in enumerate(self.__details):
                if detail.name == name:
                    answ = wx.MessageBox(caption=' ',
                                         message=f'Хотите удалить разработку {detail.name}?',
                                         style=wx.YES_NO | wx.CENTRE,
                                         parent=self)
                    if answ == wx.YES:
                        self.main_window.saved = False
                        self.__details.pop(i)
                        self.items_list_update()
                        self.update_text()
                    break
            else:
                for i, detail in enumerate(self.__developed_details):
                    if detail.name == name:
                        answ = wx.MessageBox(caption=' ',
                                             message=f'Хотите удалить разработку {detail.name}?',
                                             style=wx.YES_NO | wx.CENTRE,
                                             parent=self)
                        if answ == wx.YES:
                            self.main_window.saved = False
                            self.__developed_details.pop(i)
                            self.items_list_update()
                            self.update_text()
                        break
        else:
            answ = wx.MessageBox(caption=' ',
                                 message=f'Хотите удалить документ {name} из всех разработок?',
                                 style=wx.YES_NO | wx.CENTRE,
                                 parent=self)
            if answ == wx.YES:
                for detail in [*self.__details, *self.__developed_details]:
                    detail.delete_document(name)
                self.main_window.saved = False
                self.items_list_update()
                self.update_text()

    def __prepare_button_click(self, event=None):
        """Нажатие кнопки готовности"""
        name = self.__items_list.GetStringSelection()
        if not name:
            return
        if self.__radio_button_1.GetValue():
            for detail in [*self.__details, *self.__developed_details]:
                if detail.name == name:
                    if detail.ready:
                        detail.unprocess()
                        self.__details.append(self.__developed_details.pop(self.__developed_details.index(detail)))
                        self.__preparedness_button.SetLabel('Разработка не готова')
                        self.main_window.saved = False
                        self.update_text()
                        self.items_list_update()
                    else:
                        if detail.check_preparedness():
                            detail.process()
                            self.__developed_details.append(self.__details.pop(self.__details.index(detail)))
                            self.__preparedness_button.SetLabel('Разработка готова')
                            self.main_window.saved = False
                            self.update_text()
                            self.items_list_update()
                        else:
                            wx.MessageBox(caption='Ошибка',
                                          message='Не все документы готовы для разработки',
                                          style=wx.OK | wx.CENTRE | wx.ICON_WARNING,
                                          parent=self)
                    return
        else:
            value = bool(self.__preparedness_button.GetValue())
            for detail in [*self.__details, *self.__developed_details]:
                if name in detail.get_state():
                    detail.set_state({name: value})
            self.__preparedness_button.SetLabel(
                'Документ готов' if value else 'Документ не готов')
            self.main_window.saved = False
            self.update_text((name, value))

    def __delete_2(self, event=None):
        """Удаление документа из разработки"""
        detail_name = doc = None
        if self.__radio_button_1.GetValue():
            detail_name = self.__items_list.GetStringSelection()
            doc = self.__items_info_list.GetStringSelection()
        else:
            doc = self.__items_list.GetStringSelection()
            detail_name = self.__items_info_list.GetStringSelection()
        if not (doc and detail_name):
            return
        for detail in [*self.__details, *self.__developed_details]:
            if detail.name == detail_name:
                answ = wx.MessageBox(caption=' ',
                                     message=f'Хотите удалить документ {doc} из разработки {detail.name}?',
                                     style=wx.YES_NO | wx.CENTRE | wx.ICON_NONE,
                                     parent=self)
                if answ == wx.YES:
                    detail.delete_document(doc)
                    self.main_window.saved = False
                    self.items_list_update()
                    self.update_text()

    def items_list_update(self):
        """Обновление списка объектов"""
        while self.__items_list.GetCount():
            self.__items_list.Delete(0)
        if self.__radio_button_1.GetValue():
            items = []
            count = 0
            if self.__details:
                lst = [x.name for x in self.__details]
                lst.sort()
                items.extend(['• В разработке:', *lst])
                count += 1
            if self.__developed_details:
                lst = [x.name for x in self.__developed_details]
                lst.sort()
                items.extend(['• Разработаны:', *lst])
                count += 1
            self.__items_list.Append(items)
            self.__items_amount.SetLabel(f'Всего разработок: {self.__items_list.GetCount() - count}')
        else:
            items = set()
            for detail in [*self.__details, *self.__developed_details]:
                items.update(list(detail.get_state().keys()))
            items = list(items)
            items.sort()
            self.__items_list.Append(items)
            self.__items_amount.SetLabel(f'Всего документов: {self.__items_list.GetCount()}')

    def update_text(self, item=None):
        """Обновление содержимого текста"""
        text = ''
        items = []
        if type(item) == tuple:
            text += f'Документ {item[0]} {"готов" if item[1] else "не готов"}'
            count = 0
            for detail in [*self.__details, *self.__developed_details]:
                if item[0] in detail.get_state().keys():
                    count += 1
                    items.append(detail.name)
            if int(str(count)[-1:]) > 1:
                self.__static_text_info.SetLabel(f'Используется в {count} разработках:')
            elif count:
                self.__static_text_info.SetLabel(f'Используется в {count} разработке:')
            else:
                self.__static_text_info.SetLabel('В разработках не используется')
        elif type(item) == Detail:
            text += f'{item.name} {"разработана" if item.ready else "в разработке"}'
            count = len(item.get_state())
            if int(str(count)[-1:]) > 4:
                self.__static_text_info.SetLabel(f'Используется {count} документов:')
            elif count:
                self.__static_text_info.SetLabel(f'Используется {count} документ(а):')
            else:
                self.__static_text_info.SetLabel('Документы отсутствуют')
            items.extend(list(item.get_state().keys()))
        self.__info.SetValue(text)
        while self.__items_info_list.GetCount():
            self.__items_info_list.Delete(0)
        self.__items_info_list.Append(items)

    def __exit(self, event=None):
        """Выход из окна"""
        self.__info.SetValue('')
        self.__static_text_info.SetLabel('')
        while self.__items_info_list.GetCount():
            self.__items_info_list.Delete(0)
        self.main_window.set_details_combox()
        self.main_window.set_docs_combox()
        self.HideWithEffect(wx.SHOW_EFFECT_BLEND, 300)
        self.main_window.Show()
