export const ui = {
  language: {
    label: "Til",
  },
  theme: {
    switchTitle: "Mavzuni almashtirish (D)",
    toLight: "Yorug' mavzuga o'tish",
    toDark: "Qorong'i mavzuga o'tish",
  },
  runAudit: {
    running: "Ishlamoqda…",
    run: "Auditni ishga tushirish",
  },
  intake: {
    upload: "Hisobot yuklash",
    drop: "Fayllarni bu yerga tashlang yoki tanlash uchun bosing",
    formats: "CSV · XLSX · XML — har biri 25 MB gacha",
    hint: "Istagancha fayl tanlang, ularni quyida ko'rib chiqing va bitta ariza sifatida yuboring. Tugmani bosmaguningizcha hech narsa tekshirilmaydi.",
    remove: "o'chirish",
    ready_one: "{{count}} ta fayl tayyor",
    ready_other: "{{count}} ta fayl tayyor",
    sending: "Ariza yuborilmoqda…",
  },
  clearDocket: {
    trigger: "Navbatni tozalash",
    confirm_one: "Navbatni {{count}} ta arizadan tozalaysizmi?",
    confirm_other: "Navbatni {{count}} ta arizadan tozalaysizmi?",
    body: "Barcha arizalar va ular bilan yuklangan fayllar o'chiriladi. Nazorat ma'lumotlar bazasi va bosh sahifadagi matritsa o'zgarmaydi.",
    keep: "Saqlab qolish",
    clearing: "Tozalanmoqda…",
  },
  discard: {
    confirm: "O'chirish",
    keep: "Saqlash",
    srLabel: "{{docket}}-son arizani o'chirish",
  },
  search: {
    placeholder: "Bankni qidirish",
  },
  flagged: {
    label: "Faqat belgilanganlar",
  },
  verdictStamp: {
    flagged: "Belgilangan",
    noFindings: "Qoidabuzarlik yo'q",
  },
  exceptionCell: {
    noReading: "ma'lumot yo'q",
    flagged: "belgilangan",
    noFinding: "xulosa yo'q",
    caption: "{{name}} — {{outcome}}, {{score}}",
  },
  benfordPlot: {
    digitTitle:
      "{{digit}}-raqam: kuzatilgan {{observed}}%, kutilgan {{expected}}%",
    observed: "kuzatilgan",
    benford: "Benford",
    deviationCaption: "har bir raqam bo'yicha foiz punktlaridagi og'ish",
  },
  filingStatus: {
    flagged_one: "{{count}} ta belgilangan",
    flagged_other: "{{count}} ta belgilangan",
    noFindings: "Qoidabuzarlik yo'q",
  },
  dialog: {
    close: "Yopish",
  },
  toast: {
    auditComplete: "Audit yakunlandi",
    flaggedOf: "{{total}} ta bankdan {{flagged}} tasi belgilandi.",
    noFindingsAcross: "{{total}} ta bankda qoidabuzarlik topilmadi.",
    auditFailed: "Auditni ishga tushirib bo'lmadi",
    filingReceived: "{{docket}}-son ariza qabul qilindi",
    filingQueued: "U navbatda. Tekshirilgach, navbat yangilanadi.",
    filingRejected: "Ariza qabul qilinmadi",
    filingDiscarded: "{{docket}}-son ariza o'chirildi",
    filingNotDiscarded: "Arizani o'chirib bo'lmadi",
    filingsDiscarded_one: "{{count}} ariza o'chirildi",
    filingsDiscarded_other: "{{count}} ariza o'chirildi",
    supervisoryUntouched: "Nazorat ma'lumotlar bazasi o'zgarmadi.",
    docketNotCleared: "Navbat tozalanmadi",
    queryFailed: "Ma'lumotlarni yuklab bo'lmadi",
  },
}
