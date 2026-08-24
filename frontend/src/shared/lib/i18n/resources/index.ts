import { app as enApp } from "./en/app"
import { app as ruApp } from "./ru/app"
import { app as uzApp } from "./uz/app"
import { common as enCommon } from "./en/common"
import { common as ruCommon } from "./ru/common"
import { common as uzCommon } from "./uz/common"
import { ui as enUi } from "./en/ui"
import { ui as ruUi } from "./ru/ui"
import { ui as uzUi } from "./uz/ui"

export const resources = {
  en: { app: enApp, common: enCommon, ui: enUi },
  ru: { app: ruApp, common: ruCommon, ui: ruUi },
  uz: { app: uzApp, common: uzCommon, ui: uzUi },
} as const
