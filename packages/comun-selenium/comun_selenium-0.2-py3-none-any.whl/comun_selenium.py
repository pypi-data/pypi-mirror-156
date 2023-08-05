from selenium import webdriver


class Firefox(webdriver.Firefox):
    def __init__(self, options):
        super(Firefox, self).__init__(options=options)
        self.maximize_window()

    def guardar_captura(self, captura_error):
        try:
            if self is not None:
                self.save_screenshot(captura_error)
        except Exception:
            pass

    def close_driver(self):
        try:
            if self is not None:
                self.quit()
        except Exception:
            pass


class Chrome(webdriver.Chrome):
    def __init__(self, options):
        super(Chrome, self).__init__(options=options)
        self.maximize_window()

    def guardar_captura(self, captura_error):
        try:
            if self is not None:
                self.save_screenshot(captura_error)
        except Exception:
            pass

    def close_driver(self):
        try:
            if self is not None:
                self.quit()
        except Exception:
            pass




