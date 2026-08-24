export const common = {
  tests: {
    benford: {
      name: "Benford qonuni",
      about:
        "Kredit summalarining birinchi raqamlari kutilgan 30,1 / 17,6 / 12,5 % egri chizig'iga nisbatan",
    },
    threshold: {
      name: "K1 me'yori",
      about:
        "Kapital yetarliligi ko'rsatkichlari tartibga soluvchi minimal darajadan biroz yuqori o'ralganligi",
    },
    rounding: {
      name: "Dumaloq summalar",
      about: "Hisobot summalarining ishonib bo'lmaydigan nollar qatori bilan tugashi",
    },
    arithmetic: {
      name: "Aktivlar yig'indisi",
      about: "Aktivlar yakuni uning tarkibiy qismlari yig'indisiga nisbatan",
    },
    balance: {
      name: "Balans ayniyati",
      about: "Aktivlar majburiyatlarga nisbatan — buxgalteriya ayniyati",
    },
    discontinuity: {
      name: "Qatordagi uzilish",
      about: "Hisobot yili ichidagi oyma-oy sakrashlar",
    },
    windowDressing: {
      name: "Hisobot bezaklari",
      about: "Balans o'sishining hisobot davri oxiriga to'planishi",
    },
    lastDigit: {
      name: "Oxirgi raqam",
      about: "Kredit summalarining oxirgi raqamlari bir xil taqsimotga nisbatan",
    },
    unknownAbout: "Qo'shimcha statistik test",
  },
  mad: {
    close: "Yaqin moslik",
    acceptable: "Qabul qilinadi",
    marginally_acceptable: "Chegaraviy",
    nonconformity: "Mos kelmaydi",
  },
  status: {
    queued: "Navbatda",
    processing: "Tekshirilmoqda",
    done: "Tekshirildi",
    failed: "Qaytarildi",
  },
  statusNote: {
    queued: "Tekshiruvchini kutmoqda",
    processing: "Testlar davom etmoqda",
    done: "Natijalar tayyor",
    failed: "Tekshirib bo'lmadi",
  },
  time: {
    underSecond: "bir soniyadan kam",
  },
  evidence: {
    cols: {
      period: "davr",
      indicator: "ko'rsatkich",
      value: "qiymat",
      trailing_zeros: "nollar",
      transition: "oylar",
      before: "oldin",
      after: "keyin",
      growth: "o'sish",
      limit: "limit",
      margin: "zaxira",
      digit: "raqam",
      observed: "haqiqiy",
      expected: "kutilgan",
      deviation: "og'ish",
      share: "ulush",
      count: "soni",
      expected_count: "kutilgan",
      total_assets: "aktivlar",
      total_liabilities: "majburiyatlar",
      sum_of_parts: "qismlar yig'indisi",
      gap: "farq",
      gap_share: "farq %",
    },
    yes: "ha",
      blocks: {
        benford: {
          title: "Benford qonunidan chetlanish",
          summary:
            "{{digit}}-raqam summalarning {{observed}} qismida uchraydi, kutilgan {{expected}} oʻrniga, ogʻish {{deviation}}.",
        },
        threshold: {
          title: "K1 meʼyoridan biroz yuqori toʻplanish",
          summary:
            "{{total}} ta K1 qiymatidan {{flagged}} tasi tartibga soluvchi meʼyor darhol yuqorisidagi tor bandda (limit, limit+{{band}}].",
        },
        rounding: {
          title: "Aqlga sigʻmaydigan dumaloq summalar",
          summary: "{{count}} ta hisobot qiymati {{zeros}} yoki undan koʻp nol bilan tugaydi.",
        },
        arithmetic: {
          title: "Aktivlar yakuni mos kelmaydi",
          summary: "Aktivlar yakuni uning tarkibiy qismlari yigʻindisiga mos kelmaydi.",
        },
        balance: {
          title: "Aktivlar majburiyatlarga teng emas",
          summary: "Aktivlar majburiyatlardan farq qiladi — buxgalteriya ayniyati buzilgan.",
        },
        discontinuity: {
          title: "Hisobot qatoridagi uzilish",
          summary: "Aktivlar qoʻshni oylar orasida sakrab turadi.",
        },
        window_dressing: {
          title: "Davr oxiridagi koʻtarilish",
          summary: "Aktivlar hisobot yili oxiriga gʻayritabiiy oʻsadi.",
        },
        last_digit: {
          title: "Oxirgi raqam bir xil taqsimlanmagan",
          summary:
            "χ² = {{chi2}}, p = {{p}} reyestrdagi {{n}} ta kredit summasi oxirgi raqamining bir xil taqsimotiga nisbatan.",
        },
      },
  },

  verdict: {
    clean: "Bank dossiyesidagi hech bir test ishlamadi. Barcha {{count}} test xulosasiz o'tdi.",
    fired: "{{count}} testdan {{fired}} tasi xulosa qaytardi: {{names}}.",
    madFlagged:
      "O'rtacha mutlaq og'ish {{mad}} Nigrini chegarasi {{limit}} dan yuqori, demak birinchi raqamlar {{label}} deb o'qiladi — bunday tarqalish oddiy kreditlashdan kelib chiqishi dargumon.",
    madClean:
      "O'rtacha mutlaq og'ish {{mad}} Nigrini chegarasi {{limit}} dan past, demak birinchi raqamlar qonunga mos: {{label}}.",
    chiReject: "χ² muvofiqlikni {{level}}% darajada rad etadi (p = {{p}}).",
    chiAccept: "χ² muvofiqlikni rad etmaydi (p = {{p}}).",
  },
  errors: {
    generic: "Nimadir noto'g'ri ketdi",
    network: "API javob bermayapti — :8000 da ishlayotganini tekshiring",
    http: "HTTP {{status}} {{statusText}}",
  },
}
