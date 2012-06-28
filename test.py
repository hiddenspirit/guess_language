#!/usr/bin/env python3
"""Test suite for guess_language
"""
#   © 2012 spirit <hiddenspirit@gmail.com>
#   Copyright (c) 2008, Kent S Johnson
#
#   This program is free software: you can redistribute it and/or modify it
#   under the terms of the GNU Lesser General Public License as published
#   by the Free Software Foundation, either version 3 of the License,
#   or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#   See the GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program. If not, see <http://www.gnu.org/licenses/>.

import itertools
import unittest
import warnings

from guess_language import *
from guess_language.guess_language import (
    create_ordered_model, find_runs,
    normalize, UNKNOWN, BLOCKS, BLOCK_RSHIFT,
    enchant, _identify_by_spellchecking
)


class GuessLanguageTest(unittest.TestCase):
    tests = [
        ("This is a test of the language checker.", "en"),
        ("Vérifions que le détecteur de langue fonctionne.", "fr"),
        ("Sprawdźmy, czy odgadywacz języków pracuje", "pl"),
        ("авай проверить  узнает ли наш угадатель русски язык", "ru"),
        ("La respuesta de los acreedores a la oferta argentina para salir "
         "del default no ha sido muy positiv", "es"),
        ("Сайлау нәтижесінде дауыстардың басым бөлігін ел премьер "
         "министрі Виктор Янукович пен оның қарсыласы, оппозиция "
         "жетекшісі Виктор Ющенко алды.", "kk"),
        ("милиция ва уч солиқ идораси ходимлари яраланган. Шаҳарда "
         "хавфсизлик чоралари кучайтирилган.", "uz"),
        ("көрбөгөндөй элдик толкундоо болуп, Кокон шаарынын көчөлөрүндө "
         "бир нече миң киши нааразылык билдирди.", "ky"),
        ("yakın tarihin en çekişmeli başkanlık seçiminde oy verme işlemi "
         "sürerken, katılımda rekor bekleniyor.", "tr"),
        ("Daxil olan xəbərlərdə deyilir ki, 6 nəfər Bağdadın mərkəzində "
         "yerləşən Təhsil Nazirliyinin binası yaxınlığında baş vermiş "
         "partlayış zamanı həlak olub.", "az"),
        (" ملايين الناخبين الأمريكيين يدلون بأصواتهم وسط إقبال قياسي على "
         "انتخابات هي الأشد تنافسا منذ عقود", "ar"),
        ("Американське суспільство, поділене суперечностями, збирається "
         "взяти активну участь у голосуванні", "uk"),
        ("Francouzský ministr financí zmírnil výhrady vůči nízkým "
         "firemním daním v nových členských státech EU", "cs"),
        ("biće prilično izjednačena, sugerišu najnovije ankete. "
         "Oba kandidata tvrde da su sposobni da dobiju rat protiv "
         "terorizma", "hr"),
        (" е готов да даде гаранции, че няма да прави ядрено оръжие, "
         "ако му се разреши мирна атомна програма", "bg"),
        ("на јавното мислење покажуваат дека трката е толку тесна, "
         "што се очекува двајцата соперници да ја прекршат традицијата "
         "и да се појават и на самиот изборен ден.", "mk"),
        ("în acest sens aparţinînd Adunării Generale a organizaţiei, "
         "în ciuda faptului că mai multe dintre solicitările organizaţiei "
         "privind organizarea scrutinului nu au fost soluţionate", "ro"),
        ("kaluan ditën e fundit të fushatës në shtetet kryesore "
         "për të siguruar sa më shumë votues.", "sq"),
        ("αναμένεται να σπάσουν παράδοση δεκαετιών και να συνεχίσουν "
         "την εκστρατεία τους ακόμη και τη μέρα των εκλογών", "el"),
        (" 美国各州选民今天开始正式投票。据信，", "zh"),
        (" Die kritiek was volgens hem bitter hard nodig, "
         "omdat Nederland binnen een paar jaar in een soort Belfast zou "
         "dreigen te veranderen", "nl"),
        ("På denne side bringer vi billeder fra de mange forskellige "
         "forberedelser til arrangementet, efterhånden som vi får dem ",
         "da"),
        ("Vi säger att Frälsningen är en gåva till alla, fritt och för "
         "intet.  Men som vi nämnt så finns det två villkor som måste",
         "sv"),
        ("Nominasjonskomiteen i Akershus KrF har skviset ut Einar Holstad "
         "fra stortingslisten. Ytre Enebakk-mannen har plass p Stortinget "
         "s lenge Valgerd Svarstad Haugland sitter i", "nb"),
        ("on julkishallinnon verkkopalveluiden yhteinen osoite. "
         "Kansalaisten arkielämää helpottavaa tietoa on koottu eri "
         "aihealueisiin", "fi"),
        ("Ennetamaks reisil ebameeldivaid vahejuhtumeid vii end kurssi "
         "reisidokumentide ja viisade reeglitega ning muu praktilise "
         "informatsiooniga", "et"),
        ("Hiába jön létre az önkéntes magyar haderő, hiába nem lesz "
         "többé bevonulás, változatlanul fennmarad a hadkötelezettség "
         "intézménye", "hu"),
        ("հարաբերական", "hy"),
        ("Hai vấn đề khó chịu với màn hình thường gặp nhất khi bạn dùng "
         "laptop là vết trầy xước và điểm chết. Sau đây là vài cách xử "
         "lý chúng.", "vi"),
        ("トヨタ自動車、フィリピンの植林活動で第三者認証取得　"
         "トヨタ自動車(株)（以下、トヨタ）は、2007年９月よりフィリピンのルソン"
         "島北部に位置するカガヤン州ペニャブランカ町", "ja"),
        ("ii", UNKNOWN),
    ]

    enchant_tests = [
        ("Guess the language!", "en"),
    ]

    def test_normalize(self):
        self.assertEqual(normalize("abc4def   !@#!#@$   ghi"), "abc def ghi")

        s = ("På denne side bringer vi billeder fra de mange forskellige "
             "forberedelser til arrangementet efterhånden som vi får dem ")
        self.assertEqual(normalize(s), s)

    def test_find_runs(self):
        self.assertEqual(
            find_runs("This is a test of the language checker"),
            ["Basic Latin"]
        )
        self.assertEqual(
            set(find_runs("abcdééé")),
            set(["Basic Latin", "Extended Latin"])
        )

        s = ("Сайлау нәтижесінде дауыстардың басым бөлігін ел премьер "
             "министрі Виктор Янукович пен оның қарсыласы, оппозиция "
             "жетекшісі Виктор Ющенко алды.")
        self.assertEqual(find_runs(s), ["Cyrillic"])

    def test_create_ordered_model(self):
        self.assertEqual(create_ordered_model("abc"), ["abc"])
        self.assertEqual(create_ordered_model("abca"), ["abc", "bca"])
        self.assertEqual(
            create_ordered_model("abcabdcab"),
            ["cab", "abc", "abd", "bca", "bdc", "dca"]
        )

    def test_guess(self):
        for text, name in self.tests:
            self.assertEqual(guess_language(text), name)

        text = "Vérifions que le détecteur de langue fonctionne."
        self.assertEqual(guess_language_tag(text), "fr")
        self.assertEqual(guess_language_name(text), "French")
        self.assertEqual(guess_language_id(text), 26150)
        self.assertEqual(guess_language_info(text), ("fr", 26150, "French"))

    if enchant:
        def test_guess_enchant(self):
            languages = set(enchant.list_languages())
            self.assertNotEqual(len(languages), 0)

            for text, name in self.enchant_tests:
                self.assertEqual(guess_language(text), name)

            for text, name in self.tests:
                if name in languages:
                    self.assertEqual(_identify_by_spellchecking(text), name)
    else:
        warnings.warn("PyEnchant is unavailable")


class BlocksTest(unittest.TestCase):
    def test_unicode_block(self):
        for n in range(128):
            self.assert_block(n, "Basic Latin")

        for n in itertools.chain(range(0x80, 0x180), range(0x250, 0x2b0)):
            self.assert_block(n, "Extended Latin")

        self.assert_block(0xe00, "Thai")
        self.assert_block(0xe7f, "Thai")
        self.assert_block(0xe80, "Lao")
        self.assert_block(0xeff, "Lao")
        self.assert_block(0xf00, "Tibetan")
        self.assert_block(0xfff, "Tibetan")
        self.assert_block(0x421, "Cyrillic")

    def assert_block(self, n, name):
        block = BLOCKS[n >> BLOCK_RSHIFT]
        self.assertEqual(block, name)


if __name__ == "__main__":
    unittest.main()
