export type DisplayCurrency = "USD" | "TRY";

export const DEFAULT_USD_TO_TRY = 45.22;

const localeByCurrency: Record<DisplayCurrency, string> = {
  USD: "en-US",
  TRY: "tr-TR"
};

export function convertMoney(value: number, currency: DisplayCurrency, usdToTry = DEFAULT_USD_TO_TRY) {
  return currency === "TRY" ? value * usdToTry : value;
}

export function formatMoney(
  value: number,
  currency: DisplayCurrency,
  usdToTry = DEFAULT_USD_TO_TRY,
  maximumFractionDigits = 0
) {
  return new Intl.NumberFormat(localeByCurrency[currency], {
    style: "currency",
    currency,
    maximumFractionDigits
  }).format(convertMoney(value || 0, currency, usdToTry));
}
