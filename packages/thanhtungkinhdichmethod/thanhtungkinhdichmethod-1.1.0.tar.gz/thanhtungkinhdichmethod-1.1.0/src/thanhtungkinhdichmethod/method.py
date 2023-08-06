def TenQueTrung(thuong, ha):
    ten = [["THUẦN CÀN", "THIÊN TRẠCH LÝ", "THIÊN HỎA ĐỒNG NHÂN", "THIÊN LÔI VÔ VỌNG", "THIÊN PHONG CẤU", "THIÊN THỦY TỤNG", "THIÊN SƠN ĐỘN", "THIÊN ĐỊA BĨ"],
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
    mang = ["CÀN", "ĐOÀI", "LY", "CHẤN", "TỐN", "KHẢM", "CẤN", "KHÔN"]
    ketqua = ten[mang.index(thuong)][mang.index(ha)]
    return ketqua


def QueBienTuQueDon(que, dong1, dong2, dong3):

    dong = dong1 * 1 + dong2 * 2 + dong3 * 4
    mang = ["CÀN", "ĐOÀI", "LY", "CHẤN", "TỐN", "KHẢM", "CẤN", "KHÔN"]
    bien = [["CÀN", "TỐN", "LY", "CẤN", "ĐOÀI", "KHẢM", "CHẤN", "KHÔN"],
            ["ĐOÀI", "KHẢM", "CHẤN", "KHÔN", "CÀN", "TỐN", "LY", "CẤN"],
            ["LY", "CẤN", "CÀN", "TỐN", "CHẤN", "KHÔN", "ĐOÀI", "KHẢM"],
            ["CHẤN", "KHÔN", "ĐOÀI", "KHẢM", "LY", "CẤN", "CÀN", "TỐN"],
            ["TỐN", "CÀN", "CẤN", "LY", "KHẢM", "ĐOÀI", "KHÔN", "CHẤN"],
            ["KHẢM", "ĐOÀI", "KHÔN", "CHẤN", "TỐN", "CÀN", "CẤN", "LY"],
            ["CẤN", "LY", "TỐN", "CÀN", "KHÔN", "CHẤN", "KHẢM", "ĐOÀI"],
            ["KHÔN", "CHẤN", "KHẢM", "ĐOÀI", "CẤN", "LY", "TỐN", "CÀN"]]
    return bien[mang.index(que)][dong]


def TenQueDon(hao1, hao2, hao3):
    mangque = ["CÀN", "ĐOÀI", "LY", "CHẤN", "TỐN", "KHẢM", "CẤN", "KHÔN"]
    str_num = ["111", "110", "101", "100", "011", "010", "001", "000"]
    return mangque[str_num.index(str(hao1) + str(hao2) + str(hao3))]


def CungGoc(que):
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


def DiaChiToanQue(thuong, ha):

    diachi = [["TÝ", "DẦN", "THÌN", "NGỌ", "THÂN", "TUẤT"],
              ["TỊ", "MÃO", "SỬU", "HỢI", "DẬU", "MÙI"],
              ["MÃO", "SỬU", "HỢI", "DẬU", "MÙI", "TỊ"],
              ["TÝ", "DẦN", "THÌN", "NGỌ", "THÂN", "TUẤT"],
              ["SỬU", "HỢI", "DẬU", "MÙI", "TỊ", "MÃO"],
              ["DẦN", "THÌN", "NGỌ", "THÂN", "TUẤT", "TÝ"],
              ["THÌN", "NGỌ", "THÂN", "TUẤT", "TÝ", "DẦN"],
              ["MÙI", "TỊ", "MÃO", "SỬU", "HỢI", "DẬU"]]
    mang = ["CÀN", "ĐOÀI", "LY", "CHẤN", "TỐN", "KHẢM", "CẤN", "KHÔN"]
    ketqua = ["", "", "", "", "", ""]
    for i in range(3):
        ketqua[i] = diachi[mang.index(ha)][i]
        ketqua[i + 3] = diachi[mang.index(thuong)][i + 3]

    return ketqua


def CanQueThuong(quethuong):
    list = ["CÀN", "ĐOÀI", "LY", "CHẤN", "TỐN", "KHẢM", "CẤN", "KHÔN"]
    canque = ["NHÂM", "ĐINH", "KỶ", "CANH", "TÂN", "MẬU", "BÍNH", "QUÝ"]
    return canque[list.index(quethuong)]


def CanQueHa(queha):
    list = ["CÀN", "ĐOÀI", "LY", "CHẤN", "TỐN", "KHẢM", "CẤN", "KHÔN"]
    canque = ["GIÁP", "ĐINH", "KỶ", "CANH", "TÂN", "MẬU", "BÍNH", "ẤT"]
    return canque[list.index(queha)]


def LucThanToanQue(cungque, diachique):
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
        ketQua[i] = lucThan[sohao[i]][soCung]
    return ketQua


def LucThuToanQue(canNgay):
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
        anLucThu[i] = lucThu[int(soCanNgay)][i]

    return anLucThu


def TuanKhong(canngay, chingay):
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


def PhucThan(quechinh):
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


def HaoThe(que):
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


def HaoUng(haothe):
    the = [1, 2, 3, 4, 5, 6]
    ung = [4, 5, 6, 1, 2, 3]
    return ung[the.index(haothe)]


def AmDuongDong(hao, dong):
    li = ['00', '01', '10', '11']
    name = ['ath', 'adg', 'dth', 'ddg']
    d = str(hao)+str(dong)
    return name[li.index(d)]


def IsTheUng(tenQue, sohao):
    the = HaoThe(tenQue)
    ung = HaoUng(the)
    if(the == sohao):
        return "THẾ"
    elif(ung == sohao):
        return "ỨNG"
    else:
        return ""
