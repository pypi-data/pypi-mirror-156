def AnTenQueDich(thuong, ha):
    ketqua = "0"
    tenque = [["THUẦN CÀN", "THIÊN TRẠCH LÝ", "THIÊN HỎA ĐỒNG NHÂN", "THIÊN LÔI VÔ VỌNG", "THIÊN PHONG CẤU", "THIÊN THỦY TỤNG", "THIÊN SƠN ĐỘN", "THIÊN ĐỊA BĨ"],
              ["TRẠCH THIÊN QUẢI", "THUẦN ĐOÀI", "TRẠCH HỎA CÁCH", "TRẠCH LÔI TÙY",
               "TRẠCH PHONG ĐẠI QUÁ", "TRẠCH THỦY KHỐN", "TRẠCH SƠN HÀM", "TRẠCH ĐỊA TỤY"],
              ["HỎA THIÊN ĐẠI HỮU", "HỎA TRẠCH KHUÊ", "THUẦN LY", "HỎA LÔI PHỆ HẠP",
               "HỎA PHONG ĐỈNH", "HỎA THỦY VỊ TẾ", "HỎA SƠN LỮ", "HỎA ĐỊA TẤN"],
              ["LÔI THIÊN ĐẠI TRÁNG", "LÔI TRẠCH QUY MUỘI", "LÔI HỎA PHONG", "THUẦN CHẤN",
               "LÔI PHONG HẰNG", "LÔI THỦY GIẢI", "LÔI SƠN TIỂU QUÁ", "LÔI ĐỊA DỰ"],
              ["PHONG THIÊN TIỂU SÚC", "PHONG TRẠCH TRUNG PHU", "PHONG HỎA GIA NHÂN",
               "PHONG LÔI ÍCH", "THUẦN TỐN", "PHONG THỦY HOÁN", "PHONG SƠN TIỆM", "PHONG ĐỊA QUAN"],
              ["THỦY THIÊN NHU", "THỦY TRẠCH TIẾT", "THỦY HỎA KÝ TẾ", "THỦY LÔI TRUÂN",
               "THỦY PHONG TỈNH", "TẬP KHẢM", "THỦY SƠN KIỂN", "THỦY ĐỊA TỶ"],
              ["SƠN THIÊN ĐẠI SÚC", "SƠN TRẠCH TỔN", "SƠN HỎA BÍ", "SƠN LÔI DI",
               "SƠN PHONG CỔ", "SƠN THỦY MÔNG", "THUẦN CẤN", "SƠN ĐỊA BÁC"],
              ["ĐỊA THIÊN THÁI", "ĐỊA TRẠCH LÂM", "ĐỊA HỎA MINH DI", "ĐỊA LÔI PHỤC", "ĐỊA PHONG THĂNG", "ĐỊA THỦY SƯ", "ĐỊA SƠN KHIÊM", "THUẦN KHÔN"]]
    mangque = ["CÀN", "ĐOÀI", "LY", "CHẤN", "TỐN", "KHẢM", "CẤN", "KHÔN"]
    soque = [0, 1, 2, 3, 4, 5, 6, 7]
    soquethuong = 0
    soqueha = 0
    for i in range(8):
        if(thuong == mangque[i]):
            break
            soquethuong = i+1
    for i in range(8):
        if(ha == mangque[i]):
            break
            soqueha = i+1
    ketqua = tenque[soquethuong, soqueha]
    return ketqua


def TimQueBienDon(que, dongno1, dongno2, dongno3):

    quebien = "0"
    dongno = dongno1 * 1 + dongno2 * 2 + dongno3 * 4
    bienCAN = ["CÀN", "TỐN", "LY", "CẤN", "ĐOÀI", "KHẢM", "CHẤN", "KHÔN"]
    bienDOAI = ["ĐOÀI", "KHẢM", "CHẤN", "KHÔN", "CÀN", "TỐN", "LY", "CẤN"]
    bienLY = ["LY", "CẤN", "CÀN", "TỐN", "CHẤN", "KHÔN", "ĐOÀI", "KHẢM"]
    bienCHAN = ["CHẤN", "KHÔN", "ĐOÀI", "KHẢM", "LY", "CẤN", "CÀN", "TỐN"]
    bienTON = ["TỐN", "CÀN", "CẤN", "LY", "KHẢM", "ĐOÀI", "KHÔN", "CHẤN"]
    bienKHAM = ["KHẢM", "ĐOÀI", "KHÔN", "CHẤN", "TỐN", "CÀN", "CẤN", "LY"]
    bienCANS = ["CẤN", "LY", "TỐN", "CÀN", "KHÔN", "CHẤN", "KHẢM", "ĐOÀI"]
    bienKHON = ["KHÔN", "CHẤN", "KHẢM", "ĐOÀI", "CẤN", "LY", "TỐN", "CÀN"]
    if (que == "CÀN"):
        quebien = bienCAN[dongno]
    if (que == "ĐOÀI"):
        quebien = bienDOAI[dongno]
    if (que == "LY"):
        quebien = bienLY[dongno]
    if (que == "CHẤN"):
        quebien = bienCHAN[dongno]
    if (que == "TỐN"):
        quebien = bienTON[dongno]
    if (que == "KHẢM"):
        quebien = bienKHAM[dongno]
    if (que == "CẤN"):
        quebien = bienCANS[dongno]
    if (que == "KHÔN"):
        quebien = bienKHON[dongno]
    return quebien


def LayTenQueDonTuCacHao(haothu1, haothu2, haothu3):
    mangque = ["CÀN", "ĐOÀI", "LY", "CHẤN", "TỐN", "KHẢM", "CẤN", "KHÔN"]
    hopso = ["111", "110", "101", "100", "011", "010", "001", "000"]
    soque = str(haothu1) + str(haothu2) + str(haothu3)
    number = hopso.index(soque)
    return mangque[number]


def AnCungGocChoQue(que):
    socung = 0
    socungque = ["CUNG CÀN", "CUNG ĐOÀI", "CUNG LY", "CUNG CHẤN",
                 "CUNG TỐN", "CUNG KHẢM", "CUNG CẤN", "CUNG KHÔN"]
    tenque = [
        ["THUẦN CÀN", "THIÊN PHONG CẤU", "THIÊN SƠN ĐỘN", "THIÊN ĐỊA BĨ",
         "PHONG ĐỊA QUAN", "SƠN ĐỊA BÁC", "HỎA ĐỊA TẤN", "HỎA THIÊN ĐẠI HỮU"],
        ["THUẦN ĐOÀI", "TRẠCH THỦY KHỐN", "TRẠCH ĐỊA TỤY", "TRẠCH SƠN HÀM",
         "THỦY SƠN KIỂN", "ĐỊA SƠN KHIÊM", "LÔI SƠN TIỂU QUÁ", "LÔI TRẠCH QUY MUỘI"],
        ["THUẦN LY", "HỎA SƠN LỮ", "HỎA PHONG ĐỈNH", "HỎA THỦY VỊ TẾ", "SƠN THỦY MÔNG",
         "PHONG THỦY HOÁN", "THIÊN THỦY TỤNG", "THIÊN HỎA ĐỒNG NHÂN"],
        ["THUẦN CHẤN", "LÔI ĐỊA DỰ", "LÔI THỦY GIẢI", "LÔI PHONG HẰNG",
         "ĐỊA PHONG THĂNG", "THỦY PHONG TỈNH", "TRẠCH PHONG ĐẠI QUÁ", "TRẠCH LÔI TÙY"],
        ["THUẦN TỐN", "PHONG THIÊN TIỂU SÚC", "PHONG HỎA GIA NHÂN", "PHONG LÔI ÍCH",
         "THIÊN LÔI VÔ VỌNG", "HỎA LÔI PHỆ HẠP", "SƠN LÔI DI", "SƠN PHONG CỔ"],
        ["TẬP KHẢM", "THỦY TRẠCH TIẾT", "THỦY LÔI TRUÂN", "THỦY HỎA KÝ TẾ",
         "TRẠCH HỎA CÁCH", "LÔI HỎA PHONG", "ĐỊA HỎA MINH DI", "ĐỊA THỦY SƯ"],
        ["THUẦN CẤN", "SƠN HỎA BÍ", "SƠN THIÊN ĐẠI SÚC", "SƠN TRẠCH TỔN",
         "HỎA TRẠCH KHUÊ", "THIÊN TRẠCH LÝ", "PHONG TRẠCH TRUNG PHU", "PHONG SƠN TIỆM"],
        ["THUẦN KHÔN", "ĐỊA LÔI PHỤC", "ĐỊA TRẠCH LÂM", "ĐỊA THIÊN THÁI", "LÔI THIÊN ĐẠI TRÁNG", "TRẠCH THIÊN QUẢI", "THỦY THIÊN NHU", "THỦY ĐỊA TỶ"]]
    for i in range(8):
        for j in range(8):
            if que == tenque[i][j]:
                socung = i
    if socung > 7:
        socung = 0
    return socungque[socung]


def DuHonQuyHon(que):
    tenque = [["THUẦN CÀN", "THIÊN PHONG CẤU", "THIÊN SƠN ĐỘN", "THIÊN ĐỊA BĨ", "PHONG ĐỊA QUAN", "SƠN ĐỊA BÁC", "HỎA ĐỊA TẤN", "HỎA THIÊN ĐẠI HỮU"],
              ["THUẦN ĐOÀI", "TRẠCH THỦY KHỐN", "TRẠCH ĐỊA TỤY", "TRẠCH SƠN HÀM",
               "THỦY SƠN KIỂN", "ĐỊA SƠN KHIÊM", "LÔI SƠN TIỂU QUÁ", "LÔI TRẠCH QUY MUỘI"],
              ["THUẦN LY", "HỎA SƠN LỮ", "HỎA PHONG ĐỈNH", "HỎA THỦY VỊ TẾ", "SƠN THỦY MÔNG",
               "PHONG THỦY HOÁN", "THIÊN THỦY TỤNG", "THIÊN HỎA ĐỒNG NHÂN"],
              ["THUẦN CHẤN", "LÔI ĐỊA DỰ", "LÔI THỦY GIẢI", "LÔI PHONG HẰNG",
               "ĐỊA PHONG THĂNG", "THỦY PHONG TỈNH", "TRẠCH PHONG ĐẠI QUÁ", "TRẠCH LÔI TÙY"],
              ["THUẦN TỐN", "PHONG THIÊN TIỂU SÚC", "PHONG HỎA GIA NHÂN", "PHONG LÔI ÍCH",
               "THIÊN LÔI VÔ VỌNG", "HỎA LÔI PHỆ HẠP", "SƠN LÔI DI", "SƠN PHONG CỔ"],
              ["TẬP KHẢM", "THỦY TRẠCH TIẾT", "THỦY LÔI TRUÂN", "THỦY HỎA KÝ TẾ",
               "TRẠCH HỎA CÁCH", "LÔI HỎA PHONG", "ĐỊA HỎA MINH DI", "ĐỊA THỦY SƯ"],
              ["THUẦN CẤN", "SƠN HỎA BÍ", "SƠN THIÊN ĐẠI SÚC", "SƠN TRẠCH TỔN",
               "HỎA TRẠCH KHUÊ", "THIÊN TRẠCH LÝ", "PHONG TRẠCH TRUNG PHU", "PHONG SƠN TIỆM"],
              ["THUẦN KHÔN", "ĐỊA LÔI PHỤC", "ĐỊA TRẠCH LÂM", "ĐỊA THIÊN THÁI", "LÔI THIÊN ĐẠI TRÁNG", "TRẠCH THIÊN QUẢI", "THỦY THIÊN NHU", "THỦY ĐỊA TỶ"]]
    stt = 0
    ketqua = ""
    for i in range(8):
        for j in range(8):
            if que == tenque[i][j]:
                stt = j
    if stt == 6:
        ketqua = "Du hồn"
    elif stt == 7:
        ketqua = "Quy hồn"
    else:
        ketqua = ""
    return ketqua


def LayDiaChiChoQue(quethuong, queha):
    diachique = [["TÝ", "DẦN", "THÌN", "NGỌ", "THÂN", "TUẤT"],
                 ["TỊ", "MÃO", "SỬU", "HỢI", "DẬU", "MÙI"],
                 ["MÃO", "SỬU", "HỢI", "DẬU", "MÙI", "TỊ"],
                 ["TÝ", "DẦN", "THÌN", "NGỌ", "THÂN", "TUẤT"],
                 ["SỬU", "HỢI", "DẬU", "MÙI", "TỊ", "MÃO"],
                 ["DẦN", "THÌN", "NGỌ", "THÂN", "TUẤT", "TÝ"],
                 ["THÌN", "NGỌ", "THÂN", "TUẤT", "TÝ", "DẦN"],
                 ["MÙI", "TỊ", "MÃO", "SỬU", "HỢI", "DẬU"]]

    ketqua = ["", "", "", "", "", ""]
    for i in range(3):
        if (quethuong == "CÀN"):
            ketqua[i + 3] = diachique[0][i + 3]
        if (quethuong == "ĐOÀI"):
            ketqua[i + 3] = diachique[1][i + 3]
        if (quethuong == "LY"):
            ketqua[i + 3] = diachique[2][i + 3]
        if (quethuong == "CHẤN"):
            ketqua[i + 3] = diachique[3][i + 3]
        if (quethuong == "TỐN"):
            ketqua[i + 3] = diachique[4][i + 3]
        if (quethuong == "KHẢM"):
            ketqua[i + 3] = diachique[5][i + 3]
        if (quethuong == "CẤN"):
            ketqua[i + 3] = diachique[6][i + 3]
        if (quethuong == "KHÔN"):
            ketqua[i + 3] = diachique[7][i + 3]

    for i in range(3):
        if (queha == "CÀN"):
            ketqua[i] = diachique[0][i]
        if (queha == "ĐOÀI"):
            ketqua[i] = diachique[1][i]
        if (queha == "LY"):
            ketqua[i] = diachique[2][i]
        if (queha == "CHẤN"):
            ketqua[i] = diachique[3][i]
        if (queha == "TỐN"):
            ketqua[i] = diachique[4][i]
        if (queha == "KHẢM"):
            ketqua[i] = diachique[5][i]
        if (queha == "CẤN"):
            ketqua[i] = diachique[6][i]
        if (queha == "KHÔN"):
            ketqua[i] = diachique[7][i]

    return ketqua


def NapCanQueThuong(quethuong):
    list = ["CÀN", "ĐOÀI", "LY", "CHẤN", "TỐN", "KHẢM", "CẤN", "KHÔN"]
    canque = ["NHÂM", "ĐINH", "KỶ", "CANH", "TÂN", "MẬU", "BÍNH", "QUÝ"]
    return canque[list.index(quethuong)]


def NapCanQueHa(queha):
    list = ["CÀN", "ĐOÀI", "LY", "CHẤN", "TỐN", "KHẢM", "CẤN", "KHÔN"]
    canque = ["GIÁP", "ĐINH", "KỶ", "CANH", "TÂN", "MẬU", "BÍNH", "ẤT"]
    return canque[list.index(queha)]


def AnLucThanChoHaoQue(cungque, diachique):
    ketQua = ["", "", "", "", "", ""]
    listCung = ["CUNG CÀN", "CUNG ĐOÀI", "CUNG LY", "CUNG CHẤN",
                "CUNG TỐN", "CUNG KHẢM", "CUNG CẤN", "CUNG KHÔN"]
    number = [3, 3, 1, 2, 2, 0, 4, 4]
    diaChi = ["TÝ", "SỬU", "DẦN", "MÃO", "THÌN", "TỊ",
              "NGỌ", "MÙI", "THÂN", "DẬU", "TUẤT", "HỢI"]
    soChi = [0, 4, 2, 2, 4, 1, 1, 4, 3, 3, 4, 0]
    lucThan = [["Huynh đệ", "Quan quỷ", "Phụ mẫu", "Tử tôn", "Thê tài"],
               ["Thê tài", "Huynh đệ", "Tử tôn", "Quan quỷ", "Phụ mẫu"],
               ["Tử tôn", "Phụ mẫu", "Huynh đệ", "Thê tài", "Quan quỷ"],
               ["Phụ mẫu", "Thê tài", "Quan quỷ", "Huynh đệ", "Tử tôn"],
               ["Quan quỷ", "Tử tôn", "Thê tài", "Phụ mẫu", "Huynh đệ"],
               ]
    sohao = [0, 0, 0, 0, 0, 0]

    soCung = number[listCung.index(cungque)]
    for i in range(6):
        sohao[i] = soChi[diaChi.index(diachique[i])]

    for i in range(6):
        ketQua[i] = lucThan[sohao[i], soCung]
    return ketQua


def AnLucThu(canNgay):
    lucThu = [["Thanh long", "Chu tước", "Câu trần", "Đằng xà", "Bạch hổ", "Huyền vũ"],
              ["Chu tước", "Câu trần", "Đằng xà",
               "Bạch hổ", "Huyền vũ", "Thanh long"],
              ["Câu trần", "Đằng xà", "Bạch hổ",
               "Huyền vũ", "Thanh long", "Chu tước"],
              ["Đằng xà", "Bạch hổ", "Huyền vũ",
               "Thanh long", "Chu tước", "Câu trần"],
              ["Bạch hổ", "Huyền vũ", "Thanh long",
               "Chu tước", "Câu trần", "Đằng xà"],
              ["Huyền vũ", "Thanh long", "Chu tước",
               "Câu trần", "Đằng xà", "Bạch hổ"]
              ]
    canGoc = ["GIÁP", "ẤT", "BÍNH", "ĐINH",
              "MẬU", "KỶ", "CANH", "TÂN", "NHÂM", "QUÝ"]
    soCanNgay = 0
    soCan = canGoc.index(canNgay)
    if (soCan % 2 == 0):
        soCanNgay = soCan / 2
    else:
        soCanNgay = (soCan - 1) / 2
    anLucThu = ["", "", "", "", "", ""]
    for i in range(len(anLucThu)):
        anLucThu[i] = lucThu[soCanNgay][i]

    return anLucThu


def AnTuanKhong(canngay, chingay):
    can = ["GIÁP", "ẤT", "BÍNH", "ĐINH",
           "MẬU", "KỶ", "CANH", "TÂN", "NHÂM", "QUÝ"]
    chi = ["TÝ", "SỬU", "DẦN", "MÃO", "THÌN",
           "TỊ", "NGỌ", "MÙI", "THÂN", "DẬU", "TUẤT", "HỢI"]
    socan = can.index(canngay)
    sochi = chi.index(chingay)
    tuankhong = [["TUẤT, HỢI", "", "TÝ, SỬU", "", "DẦN, MÃO", "",
                  "THÌN, TỊ", "", "NGỌ, MÙI", "", "THÂN, DẬU", ""],
                 ["", "TUẤT, HỢI", "", "TÝ, SỬU", "", "DẦN, MÃO", "",
                  "THÌN, TỊ", "", "NGỌ, MÙI", "", "THÂN, DẬU"],
                 ["THÂN, DẬU", "", "TUẤT, HỢI", "", "TÝ, SỬU", "",
                  "DẦN, MÃO", "", "THÌN, TỊ", "", "NGỌ, MÙI", ""],
                 ["", "THÂN, DẬU", "", "TUẤT, HỢI", "", "TÝ, SỬU",
                  "", "DẦN, MÃO", "", "THÌN, TỊ", "", "NGỌ, MÙI"],
                 ["NGỌ, MÙI", "", "THÂN, DẬU", "", "TUẤT, HỢI", "",
                  "TÝ, SỬU", "", "DẦN, MÃO", "", "THÌN, TỊ", ""],
                 ["", "NGỌ, MÙI", "", "THÂN, DẬU", "", "TUẤT, HỢI",
                  "", "TÝ, SỬU", "", "DẦN, MÃO", "", "THÌN, TỊ"],
                 ["THÌN, TỊ", "", "NGỌ, MÙI", "", "THÂN, DẬU", "",
                  "TUẤT, HỢI", "", "TÝ, SỬU", "", "DẦN, MÃO", ""],
                 ["", "THÌN, TỊ", "", "NGỌ, MÙI", "", "THÂN, DẬU",
                  "", "TUẤT, HỢI", "", "TÝ, SỬU", "", "DẦN, MÃO"],
                 ["DẦN, MÃO", "", "THÌN, TỊ", "", "NGỌ, MÙI", "",
                  "THÂN, DẬU", "", "TUẤT, HỢI", "", "TÝ, SỬU", ""],
                 ["", "DẦN, MÃO", "", "THÌN, TỊ", "", "NGỌ, MÙI", "",
                  "THÂN, DẬU", "", "TUẤT, HỢI", "", "TÝ, SỬU"]
                 ]
    tk = tuankhong[socan][sochi]
    return tk


def AnPhucThan(quechinh):
    phucthan = ["", "", "", "", "", ""]
    if (quechinh == "THIÊN PHONG CẤU"):
        phucthan[1] = "(Tài DẦN)"
    if (quechinh == "THIÊN SƠN ĐỘN"):
        phucthan[0] = "(Tử TÝ)"
        phucthan[1] = "(Tài DẦN)"
    if (quechinh == "THIÊN ĐỊA BĨ"):
        phucthan[0] = "(Tử TÝ)"
    if (quechinh == "PHONG ĐỊA QUAN"):
        phucthan[0] = "(Tử TÝ)"
    if (quechinh == "SƠN ĐỊA BÁC"):
        phucthan[4] = "(Huynh THÂN)"
    if (quechinh == "HỎA ĐỊA TẤN"):
        phucthan[0] = "(Tử TÝ)"
    if (quechinh == "TRẠCH SƠN HÀM"):
        phucthan[1] = "(Tài MÃO)"
    if (quechinh == "THỦY SƠN KIỂN"):
        phucthan[1] = "(Tài MÃO)"
    if (quechinh == "ĐỊA SƠN KHIÊM"):
        phucthan[1] = "(Tài MÃO)"
    if (quechinh == "LÔI SƠN TIỂU QUÁ"):
        phucthan[1] = "(Tài MÃO)"
        phucthan[3] = "(Tử HỢI)"
    if (quechinh == "LÔI TRẠCH QUY MUỘI"):
        phucthan[3] = "(Tử HỢI)"
    if (quechinh == "HỎA SƠN LỮ"):
        phucthan[2] = "(Quan HỢI)"
        phucthan[0] = "(Phụ MÃO)"
    if (quechinh == "HỎA PHONG ĐỈNH"):
        phucthan[0] = "(Phụ MÃO)"
    if (quechinh == "HỎA THỦY VỊ TẾ"):
        phucthan[2] = "(Quan HỢI)"
    if (quechinh == "SƠN THỦY MÔNG"):
        phucthan[3] = "(Tài DẬU)"
    if (quechinh == "PHONG THỦY HOÁN"):
        phucthan[2] = "(Quan HỢI)"
        phucthan[3] = "(Tài DẬU)"
    if (quechinh == "THIÊN THỦY TỤNG"):
        phucthan[2] = "(Quan HỢI)"
    if (quechinh == "LÔI ĐỊA DỰ"):
        phucthan[0] = "(Phụ TÝ)"
    if (quechinh == "LÔI THỦY GIẢI"):
        phucthan[0] = "(Phụ TÝ)"
    if (quechinh == "LÔI PHONG HẰNG"):
        phucthan[1] = "(Huynh DẦN)"
    if (quechinh == "ĐỊA PHONG THĂNG"):
        phucthan[1] = "(Huynh DẦN)"
        phucthan[3] = ("Tử NGỌ")
    if (quechinh == "THỦY PHONG TỈNH"):
        phucthan[1] = "(Huynh DẦN)"
        phucthan[3] = ("Tử NGỌ")
    if (quechinh == "TRẠCH PHONG ĐẠI QUÁ"):
        phucthan[1] = "(Huynh DẦN)"
        phucthan[3] = ("Tử NGỌ")
    if (quechinh == "TRẠCH LÔI TÙY"):
        phucthan[3] = ("Tử NGỌ")
    if (quechinh == "PHONG THIÊN TIỂU SÚC"):
        phucthan[2] = "(Quan DẬU)"
    if (quechinh == "PHONG HỎA GIA NHÂN"):
        phucthan[2] = "(Quan DẬU)"
    if (quechinh == "PHONG LÔI ÍCH"):
        phucthan[2] = "(Quan DẬU)"
    if (quechinh == "SƠN LÔI DI"):
        phucthan[2] = "(Quan DẬU)"
        phucthan[4] = "(Tử TỊ)"
    if (quechinh == "SƠN PHONG CỔ"):
        phucthan[4] = "(Tử TỊ)"
    if (quechinh == "THỦY LÔI TRUÂN"):
        phucthan[2] = "(Tài NGỌ)"
    if (quechinh == "THỦY HỎA KÝ TẾ"):
        phucthan[2] = "(Tài NGỌ)"
    if (quechinh == "TRẠCH HỎA CÁCH"):
        phucthan[2] = "(Tài NGỌ)"
    if (quechinh == "ĐỊA HỎA MINH DI"):
        phucthan[2] = "(Tài NGỌ)"
    if (quechinh == "SƠN HỎA BÍ"):
        phucthan[2] = "(Tử THÂN)"
    if (quechinh == "SƠN THIÊN ĐẠI SÚC"):
        phucthan[1] = "(Phụ NGỌ)"
        phucthan[2] = "(Tử THÂN)"
    if (quechinh == "SƠN TRẠCH TỔN"):
        phucthan[2] = "(Tử THÂN)"
    if (quechinh == "HỎA TRẠCH KHUÊ"):
        phucthan[4] = "(Tài TÝ)"
    if (quechinh == "PHONG TRẠCH TRUNG PHU"):
        phucthan[2] = "(Tử THÂN)"
        phucthan[4] = "(Tài TÝ)"
    if (quechinh == "PHONG SƠN TIỆM"):
        phucthan[4] = "(Tài TÝ)"
    if (quechinh == "ĐỊA LÔI PHỤC"):
        phucthan[1] = "(Phụ TỊ)"
    if (quechinh == "ĐỊA THIÊN THÁI"):
        phucthan[1] = "(Phụ TỊ)"
    if (quechinh == "TRẠCH THIÊN QUẢI"):
        phucthan[1] = "(Phụ TỊ)"
    if (quechinh == "THỦY THIÊN NHU"):
        phucthan[1] = "(Phụ TỊ)"
    return phucthan


def AnTheHao(que):
    sothe = 0
    manghaothe = [6, 1, 2, 3, 4, 5, 4, 3]
    tenque = [["THUẦN CÀN", "THIÊN PHONG CẤU", "THIÊN SƠN ĐỘN", "THIÊN ĐỊA BĨ", "PHONG ĐỊA QUAN", "SƠN ĐỊA BÁC", "HỎA ĐỊA TẤN", "HỎA THIÊN ĐẠI HỮU"],
              ["THUẦN ĐOÀI", "TRẠCH THỦY KHỐN", "TRẠCH ĐỊA TỤY", "TRẠCH SƠN HÀM",
               "THỦY SƠN KIỂN", "ĐỊA SƠN KHIÊM", "LÔI SƠN TIỂU QUÁ", "LÔI TRẠCH QUY MUỘI"],
              ["THUẦN LY", "HỎA SƠN LỮ", "HỎA PHONG ĐỈNH", "HỎA THỦY VỊ TẾ", "SƠN THỦY MÔNG",
                                         "PHONG THỦY HOÁN", "THIÊN THỦY TỤNG", "THIÊN HỎA ĐỒNG NHÂN"],
              ["THUẦN CHẤN", "LÔI ĐỊA DỰ", "LÔI THỦY GIẢI", "LÔI PHONG HẰNG",
               "ĐỊA PHONG THĂNG", "THỦY PHONG TỈNH", "TRẠCH PHONG ĐẠI QUÁ", "TRẠCH LÔI TÙY"],
              ["THUẦN TỐN", "PHONG THIÊN TIỂU SÚC", "PHONG HỎA GIA NHÂN", "PHONG LÔI ÍCH",
               "THIÊN LÔI VÔ VỌNG", "HỎA LÔI PHỆ HẠP", "SƠN LÔI DI", "SƠN PHONG CỔ"],
              ["TẬP KHẢM", "THỦY TRẠCH TIẾT", "THỦY LÔI TRUÂN", "THỦY HỎA KÝ TẾ",
               "TRẠCH HỎA CÁCH", "LÔI HỎA PHONG", "ĐỊA HỎA MINH DI", "ĐỊA THỦY SƯ"],
              ["THUẦN CẤN", "SƠN HỎA BÍ", "SƠN THIÊN ĐẠI SÚC", "SƠN TRẠCH TỔN",
               "HỎA TRẠCH KHUÊ", "THIÊN TRẠCH LÝ", "PHONG TRẠCH TRUNG PHU", "PHONG SƠN TIỆM"],
              ["THUẦN KHÔN", "ĐỊA LÔI PHỤC", "ĐỊA TRẠCH LÂM", "ĐỊA THIÊN THÁI", "LÔI THIÊN ĐẠI TRÁNG", "TRẠCH THIÊN QUẢI", "THỦY THIÊN NHU", "THỦY ĐỊA TỶ"]]
    for i in range(8):
        for j in range(8):
            if que == tenque[i][j]:
                sothe = j

    return manghaothe[sothe]


def AnUngHao(haothe):
    the = [1, 2, 3, 4, 5, 6]
    ung = [4, 5, 6, 1, 2, 3]
    return ung[the.index(haothe)]
