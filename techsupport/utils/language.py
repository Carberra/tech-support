class LanguageUtility:
    LANGUAGES = {
        "C": ("h",),
        "Clojure": ("clj",),
        "C++": ("cpp", "hpp", "h++",),
        "Crystal": ("cr",),
        "C#": ("cs", "csharp",),
        "CSS": (),
        "D": (),
        "Go": ("golang",),
        "HTML": ("htm",),
        "Java": (),
        "JavaScript": ("ecma", "ecmascript", "es", "js"),
        "Julia": (),
        "Less": (),
        "Lua": (),
        "Nim": (),
        "PHP": (),
        "Python": ("py",),
        "R": (),
        "Ruby": ("rb",),
        "Rust": ("rs",),
        "Sass": ("scss",),
        "Scala": ("sc",),
        "SQL": (),
        "Swift": (),
        "TypeScript": ("ts",),
    }

    @staticmethod
    async def resolve(language_string):
        for language, aliases in LanguageUtility.LANGUAGES.items():
            if language_string.lower() in map(lambda x: x.lower(), (language, *aliases)):
                return language
