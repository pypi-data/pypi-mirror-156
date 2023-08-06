# -*- coding: utf-8 -*-

import glob
from collections import Counter
import os
import unicodedata
from timeit import repeat
from UnicodeTokenizer import UnicodeTokenizer
from BertTokenization import BasicTokenizer as BertBasicTokenizer

from setuptools import setup, find_packages
print(find_packages())

def demo(doc):
    head = ["sentence", "UnicodeTokenizer",
            "Unicode Tokens Length", "BertBasicTokenizer", "Bert Tokens length"]
    result = ['\t'.join(head)]
    for line in doc:
        tokens1 = UnicodeTokenizer.tokenize(line)
        tokens2 = BertTokenizer.tokenize(line)
        row = [line, ' '.join(tokens1), len(tokens1),
               ' '.join(tokens2), len(tokens2)]
        row = '\t'.join(str(x) for x in row)
        result.append(row)
    # result='\n'.join(result)
    print(result)
    with open("result.tsv", "w") as f:
        for row in result:
            f.write(row+'\n')


if __name__ == "__main__":

    UnicodeTokenizer = UnicodeTokenizer(do_lower_case=True, never_split=set([
        "[UNK]", "[SEP]", "[PAD]", "[CLS]", "[MASK]"]))
    BertTokenizer = BertBasicTokenizer(do_lower_case=True)

    doc = [" '〇㎡[คุณจะจัดพิธีแต่งงานเมื่อไรคะัีิ์ื็ํึ]Ⅷpays-g[ran]d-blanc-élevé » (白高大夏國)'",
           "Ⅷ首先8.88设置 st。art_new_word=True 和 output=[açaí]，output 就是最终 no such name",
           "的输出คุณจะจัดพิธีแต่งงานเมื่อไรคะ탑승 수속해야pneumonoultramicroscopicsilicovolcanoconiosis",
           "하는데 카운터가 어디에 있어요ꆃꎭꆈꌠꊨꏦꏲꅉꆅꉚꅉꋍꂷꂶꌠلأحياء تمارين تتطلب من [MASK] [PAD] [CLS][SEP]",
           '''est 𗴂𗹭𘜶𗴲𗂧, ou "phiow-bjij-lhjij-lhjij", ce que l'on peut traduire par « pays-grand-blanc-élevé » (白高大夏國).''',
           'วรรณพงษ์เป็นนักศึกษาชั้นปีที่หนึ่ง เรียนสาขาวิทยาการคอมพิวเตอร์และสารสนเทศคณะวิทยาศาสตร์ประยุกต์และวิศวกรรมศาสตร์อยู่ที่มหาวิทยาลัยขอนแก่นวิทยาเขตหนองคายยืมคืนทรัพยากรห้องสมุดเอกสารสัมมนาคอมพิวเตอร์ปัญญาประดิษฐ์กับการพัฒนาเกมแมวกินปลาหิวววไหมหลักสูตรใหม่สดสดทนได้',
           'ສົມເດັດພະເຈົ້າຢູ່ຫົວບໍຣົມໂກດຊົງທຳນຸບຳລຸງບ້ານເມືອງແລະພະສາດສະໜາຈົນກ່າວໄດ້ວ່າກຸງສີອະຍຸທະຢາໃນສະໄໝພະອົງນັ້ນເປັນຍຸກທີ່ບ້ານເມືອງດີ ມີຂຸນນາງຄົນສຳຄັນທີ່ເຕີບໂຕໃນເວລາຕໍ່ມາ ໃນລາຊະການຂອງພະອົງຫຼາຍຄົນ ເຊັ່ນ ສົມເດັດພະເຈົ້າກຸງທົນບຸລີ, ພະບາດສົມເດັດພະພຸດທະຍອດຟ້າຈຸລາໂລກມະຫາລາດ ເປັນຕົ້ນ ໃນທາງດ້ານວັນນະຄະດີກໍມີກະວີຄົນສຳຄັນ ເຊັ່ນ ເຈົ້າຟ້າທຳມາທິເບດໄຊຍະເຊດສຸລິຍະວົງ ກົມມະຂຸນເສນາພິທັກ ຫຼືເຈົ້າຟ້າກຸ້ງ ເຊິ່ງເປັນພະໂອລົດ ເປັນຕົ້ນ'
           ]
    demo(doc)


""" tokenize result 

sentence	UnicodeTokenizer	Unicode Tokens Length	BertBasicTokenizer	Bert Tokens length
 '〇㎡[คุณจะจัดพิธีแต่งงานเมื่อไรคะัีิ์ื็ํึ]Ⅷpays-g[ran]d-blanc-élevé » (白高大夏國)'	' 〇 ㎡ [ ค ณจะจ ดพ ธ แต งงานเม อไรคะ ] ⅷ pays - g [ ran ] d - blanc - eleve » ( 白 高 大 夏 國 ) '	33	' 〇㎡ [ คณจะจดพธแตงงานเมอไรคะ ] ⅷpays - g [ ran ] d - blanc - eleve » ( 白 高 大 夏 國 ) '	25
Ⅷ首先8.88设置 st。art_new_word=True 和 output=[açaí]，output 就是最终 no such name	ⅷ 首 先 8 . 88 设 置 st 。 art _ new _ word = true 和 output = [ acai ] ， output 就 是 最 终 no such name	32	ⅷ 首 先 8 . 88 设 置 st 。 art _ new _ word = true 和 output = [ acai ] ， output 就 是 最 终 no such name	32
的输出คุณจะจัดพิธีแต่งงานเมื่อไรคะ탑승 수속해야pneumonoultramicroscopicsilicovolcanoconiosis	的 输 出 ค ณจะจ ดพ ธ แต งงานเม อไรคะ 탑 승 수 속 해 야 pneumonoultramicroscopicsilicovolcanoconiosis	17	的 输 出 คณจะจดพธแตงงานเมอไรคะ탑승 수속해야pneumonoultramicroscopicsilicovolcanoconiosis	5
하는데 카운터가 어디에 있어요ꆃꎭꆈꌠꊨꏦꏲꅉꆅꉚꅉꋍꂷꂶꌠلأحياء تمارين تتطلب من [MASK] [PAD] [CLS][SEP]	하 는 데 카 운 터 가 어 디 에 있 어 요 ꆃ ꎭ ꆈ ꌠ ꊨ ꏦ ꏲ ꅉ ꆅ ꉚ ꅉ ꋍ ꂷ ꂶ ꌠ لاحياء تمارين تتطلب من [MASK] [PAD] [ cls ] [ sep ]	40	하는데 카운터가 어디에 있어요ꆃꎭꆈꌠꊨꏦꏲꅉꆅꉚꅉꋍꂷꂶꌠلاحياء تمارين تتطلب من [MASK] [PAD] [ cls ] [ sep ]	15
est 𗴂𗹭𘜶𗴲𗂧, ou "phiow-bjij-lhjij-lhjij", ce que l'on peut traduire par « pays-grand-blanc-élevé » (白高大夏國).	est 𗴂 𗹭 𘜶 𗴲 𗂧 , ou " phiow - bjij - lhjij - lhjij " , ce que l ' on peut traduire par « pays - grand - blanc - eleve » ( 白 高 大 夏 國 ) .	43	est 𗴂𗹭𘜶𗴲𗂧 , ou " phiow - bjij - lhjij - lhjij " , ce que l ' on peut traduire par « pays - grand - blanc - eleve » ( 白 高 大 夏 國 ) .	39
วรรณพงษ์เป็นนักศึกษาชั้นปีที่หนึ่ง เรียนสาขาวิทยาการคอมพิวเตอร์และสารสนเทศคณะวิทยาศาสตร์ประยุกต์และวิศวกรรมศาสตร์อยู่ที่มหาวิทยาลัยขอนแก่นวิทยาเขตหนองคายยืมคืนทรัพยากรห้องสมุดเอกสารสัมมนาคอมพิวเตอร์ปัญญาประดิษฐ์กับการพัฒนาเกมแมวกินปลาหิวววไหมหลักสูตรใหม่สดสดทนได้	วรรณพงษ เป นน กศ กษาช นป ท หน ง เร ยนสาขาว ทยาการคอมพ วเตอร และสารสนเทศคณะว ทยาศาสตร ประย กต และว ศวกรรมศาสตร อย ท มหาว ทยาล ยขอนแก นว ทยาเขตหนองคายย มค นทร พยากรห องสม ดเอกสารส มมนาคอมพ วเตอร ป ญญาประด ษฐ ก บการพ ฒนาเกมแมวก นปลาห วววไหมหล กส ตรใหม สดสดทนได	44	วรรณพงษเปนนกศกษาชนปทหนง เรยนสาขาวทยาการคอมพวเตอรและสารสนเทศคณะวทยาศาสตรประยกตและวศวกรรมศาสตรอยทมหาวทยาลยขอนแกนวทยาเขตหนองคายยมคนทรพยากรหองสมดเอกสารสมมนาคอมพวเตอรปญญาประดษฐกบการพฒนาเกมแมวกนปลาหวววไหมหลกสตรใหมสดสดทนได	2
ສົມເດັດພະເຈົ້າຢູ່ຫົວບໍຣົມໂກດຊົງທຳນຸບຳລຸງບ້ານເມືອງແລະພະສາດສະໜາຈົນກ່າວໄດ້ວ່າກຸງສີອະຍຸທະຢາໃນສະໄໝພະອົງນັ້ນເປັນຍຸກທີ່ບ້ານເມືອງດີ ມີຂຸນນາງຄົນສຳຄັນທີ່ເຕີບໂຕໃນເວລາຕໍ່ມາ ໃນລາຊະການຂອງພະອົງຫຼາຍຄົນ ເຊັ່ນ ສົມເດັດພະເຈົ້າກຸງທົນບຸລີ, ພະບາດສົມເດັດພະພຸດທະຍອດຟ້າຈຸລາໂລກມະຫາລາດ ເປັນຕົ້ນ ໃນທາງດ້ານວັນນະຄະດີກໍມີກະວີຄົນສຳຄັນ ເຊັ່ນ ເຈົ້າຟ້າທຳມາທິເບດໄຊຍະເຊດສຸລິຍະວົງ ກົມມະຂຸນເສນາພິທັກ ຫຼືເຈົ້າຟ້າກຸ້ງ ເຊິ່ງເປັນພະໂອລົດ ເປັນຕົ້ນ	ສ ມເດ ດພະເຈ າຢ ຫ ວບ ຣ ມໂກດຊ ງທຳນ ບຳລ ງບ ານເມ ອງແລະພະສາດສະໜາຈ ນກ າວໄດ ວ າກ ງສ ອະຍ ທະຢາໃນສະໄໝພະອ ງນ ນເປ ນຍ ກທ ບ ານເມ ອງດ ມ ຂ ນນາງຄ ນສຳຄ ນທ ເຕ ບໂຕໃນເວລາຕ ມາ ໃນລາຊະການຂອງພະອ ງຫ າຍຄ ນ ເຊ ນ ສ ມເດ ດພະເຈ າກ ງທ ນບ ລ , ພະບາດສ ມເດ ດພະພ ດທະຍອດຟ າຈ ລາໂລກມະຫາລາດ ເປ ນຕ ນ ໃນທາງດ ານວ ນນະຄະດ ກ ມ ກະວ ຄ ນສຳຄ ນ ເຊ ນ ເຈ າຟ າທຳມາທ ເບດໄຊຍະເຊດສ ລ ຍະວ ງ ກ ມມະຂ ນເສນາພ ທ ກ ຫ ເຈ າຟ າກ ງ ເຊ ງເປ ນພະໂອລ ດ ເປ ນຕ ນ	93	ສມເດດພະເຈາຢຫວບຣມໂກດຊງທຳນບຳລງບານເມອງແລະພະສາດສະໜາຈນກາວໄດວາກງສອະຍທະຢາໃນສະໄໝພະອງນນເປນຍກທບານເມອງດ ມຂນນາງຄນສຳຄນທເຕບໂຕໃນເວລາຕມາ ໃນລາຊະການຂອງພະອງຫາຍຄນ ເຊນ ສມເດດພະເຈາກງທນບລ , ພະບາດສມເດດພະພດທະຍອດຟາຈລາໂລກມະຫາລາດ ເປນຕນ ໃນທາງດານວນນະຄະດກມກະວຄນສຳຄນ ເຊນ ເຈາຟາທຳມາທເບດໄຊຍະເຊດສລຍະວງ ກມມະຂນເສນາພທກ ຫເຈາຟາກງ ເຊງເປນພະໂອລດ ເປນຕນ	15


"""
