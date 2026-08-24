export const app = {
  header: {
    brand: "Bank nazorati",
    tagline: "Oʻzbekiston Markaziy banki",
  },
  matrix: {
    title: "Istisnolar matritsasi",
    noMatch: "Hozirgi filtrlarga hech bir bank mos kelmaydi.",
    clearFilters: "Filtrlarni tozalash",
    tests: "Testlar",
    bank: "Bank",
    score: "Baho",
    mad: "MAD",
    pressToNarrow: "Testlar — matritsani toraytirish uchun bosing",
    rankedBy: "Umumiy baho boʻyicha tartiblangan, eng yomondan boshlab",
    fewerThan300: "300 dan kam kredit — koʻrsatkich eʼlon qilinmaydi.",
  },
  lede: {
    statisticalExceptionReport: "Statistik istisnolar hisoboti",
    banks_one: "{{count}} ta bank",
    banks_other: "{{count}} ta bank",
    loanRecords_one: "{{total}} ta kredit yozuvi",
    loanRecords_other: "{{total}} ta kredit yozuvi",
    filedLines_one: "{{total}} ta hisobot qatori",
    filedLines_other: "{{total}} ta hisobot qatori",
    prudentialReadings_one: "{{total}} ta prudensial koʻrsatkich",
    prudentialReadings_other: "{{total}} ta prudensial koʻrsatkich",
    tests_one: "{{total}} ta test",
    tests_other: "{{total}} ta test",
    failed:
      "{{total}} ta bankdan {{flagged}} tasi kamida bitta testni oʻtmadi.",
    passed: "Barcha {{banks}} ushbu yugurishdagi barcha testlardan oʻtdi.",
    sampleOk:
      "Barcha banklar n ≥ {{minSample}} minimumini bajaradi, shuning uchun Benford testi butun tanlov boʻyicha hisoblanadi.",
    sampleTooSmall: "Benford testi uchun tanlov juda kichik:",
    sampleSmallBody:
      "{{banks}} da {{minSample}} dan kam kredit yozuvlari mavjud. Ularning birinchi raqam boʻyicha koʻrsatkichi eʼlon qilinmaydi.",
  },
  caseFile: {
    title: "Bank ishi",
    navLabel: "Bank ishi",
    allBanks: "Barcha banklar",
    firstInRank: "Reytingda birinchi",
    lastInRank: "Reytingda oxirgi",
    noFileFor: "«{{bank}}» uchun ish fayli mavjud emas",
    noFileBody:
      "Oxirgi yugurishda bunday nomdagi bank mavjud emas. Auditni qayta ishga tushiring yoki istisnolar matritsasidan bank tanlang.",
    backToAllBanks: "Barcha banklarga qaytish",
    detailUnavailable: "Tafsilotlar mavjud emas.",
    detailUnavailableBody:
      "Ushbu bank boʻyicha Benford koʻrsatkichi va dalillarni yuklab boʻlmadi. Auditni qayta ishga tushirib, ishni qayta oching.",
    rank: "Bank ishi · {{rank}}-oʻrin (jami {{total}})",
    findings: "Buzilishlar",
    compositeScore: "Umumiy baho",
    loanRecords: "Kredit yozuvlari",
    firedOf: "{{fired}} tadan {{total}} tasi",
  },
  benford: {
    firstDigitConformity: "Birinchi raqamga muvofiqlik",
    verdict: "Xulosa",
    nigriniLimit: "Nigrini chegarasi",
    bootstrap95: "Bootstrap, 95-pertsentil",
    usableDropped:
      "Yaroqli kredit summalari: {{usable}}, oʻqib boʻlmaydigan yoki musbat boʻlmaganlari tashlab yuborildi: {{dropped}}.",
    notScored: "Benford boʻyicha baholanmagan.",
    insufficientBody:
      "Ushbu bank {{total}} ta yaroqli kredit summasini taqdim etdi — bu test haqiqiy ogʻishni shovqindan ajrata olishi uchun zarur boʻlgan minimal tanlovdan kam. Birinchi raqam boʻyicha koʻrsatkich eʼlon qilinmaydi, shuning uchun yuqoridagi xulosa faqat boshqa testlarga tayanadi.",
  },
  roster: {
    title: "Testlar reyestri",
    flaggedOf: "{{fired}} tadan {{total}} tasi belgilangan",
    flagged: "Belgilangan",
    clear: "Toza",
  },
  evidence: {
    title: "Dalillar",
    exhibits_one: "{{count}} ta dalil",
    exhibits_other: "{{count}} ta dalil",
    suspect: "Shubhali",
    caption:
      "{{title}} — {{total}} qatordan {{suspects}} tasi shubhali deb belgilangan",
  },
  docket: {
    title: "Arizalar jurnali",
    count_one: "{{count}} ta ariza",
    count_other: "{{count}} ta ariza",
    files_one: "{{count}} ta fayl",
    files_other: "{{count}} ta fayl",
    remarks_one: "· {{count}} ta izoh",
    remarks_other: "· {{count}} ta izoh",
    empty:
      "Hozircha arizalar yoʻq. Reyestr, prudensial normalar toʻplami yoki jamlangan hisobotni yuklang — ariza alohida tekshiriladi.",
  },
  filingMasthead: {
    filing: "Ariza {{docket}} · topshirildi {{filed}}",
    banksRead: "Tahlil qilingan banklar",
    flagged: "Belgilangan",
    files: "Fayllar",
    examinedIn: "Tekshiruv vaqti",
    bankScope_one: "{{count}} ta bank",
    bankScope_other: "{{count}} ta bank",
    clean:
      "Ushbu arizada hech bir koʻrsatkich meʼyordan oshmadi. {{scope}} tahlil qilindi va ular uchun maʼlumot boʻlgan barcha testlar toza yakunlandi.",
    flaggedSentence:
      "Ushbu arizadagi {{scope}} ichidan {{flagged}} tasi kamida bitta meʼyorni buzdi. Ular quyida, eng yomondan boshlab tartiblangan.",
    rows_one: "{{count}} ta qator",
    rows_other: "{{count}} ta qator",
  },
  filingNotes: {
    onData: "maʼlumotlar boʻyicha: {{count}}",
    testsSkipped_one: "oʻtkazib yuborilgan testlar: {{count}}",
    testsSkipped_other: "oʻtkazib yuborilgan testlar: {{count}}",
    remarks: "Izohlar",
    error: "Xato",
    warning: "Ogohlantirish",
    skippedLine_one:
      "Bitta test oʻtkazilmadi: bu arizada {{names}} uchun maʼlumot boʻlmadi.",
    skippedLine_other:
      "{{count}} ta test oʻtkazilmadi: bu arizada {{names}} uchun maʼlumot boʻlmadi.",
    skippedCoda: "Oʻtkazib yuborilgan test — oʻtgan test emas.",
    skippedPrefix: "Oʻtkazib yuborilgan · {{codes}}",
  },
  filings: {
    uploadReport: "Hisobot yuklash",
    navLabel: "Hisobot yuklash",
    supervisoryDataset: "Nazorat maʼlumotlar toʻplami",
    title: "Tekshiruv uchun hisobot topshirish",
    intro:
      "Har bir ariza navbatga qoʻyiladi, alohida tekshiriladi va qolganlaridan ajratiladi. Kredit reyestrini, prudensial normalar toʻplamini, jamlangan hisobotni — yoki uchalasini birdan yuboring; maʼlumotga ega boʻlgan testlar ishga tushadi.",
  },
  filingReport: {
    navLabel: "Ariza",
    docket: "Arizalar jurnali",
    caption: "{{docket}}-arizadagi buzilishlar",
    stillOpen: "Buzilishlar tekshiruv tugashi bilanoq shu yerda paydo boʻladi.",
    filing: "Ariza {{docket}}",
    noSuch: "Bunday ariza mavjud emas",
    noSuchBody:
      "Jurnalda bu raqam ostida ariza yoʻq. U oʻchirilgan boʻlishi mumkin. Tekshiruv uchun hisobotni qayta yuklang.",
    backToDocket: "Arizalar jurnaliga qaytish",
  },
}
