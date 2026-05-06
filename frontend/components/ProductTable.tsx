import type { ProductRow } from "@/lib/api";

export function ProductTable({
  formatMoney,
  labels,
  products
}: {
  formatMoney?: (value: number) => string;
  labels?: {
    product: string;
    revenue: string;
    cost: string;
    commission: string;
    shipping: string;
    ads: string;
    profit: string;
    margin: string;
    empty: string;
  };
  products: ProductRow[];
}) {
  const money = formatMoney || ((value: number) => `$${Math.round(value).toLocaleString("en-US")}`);

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>{labels?.product || "Product"}</th>
            <th>{labels?.revenue || "Revenue"}</th>
            <th>{labels?.cost || "Cost"}</th>
            <th>{labels?.commission || "Commission"}</th>
            <th>{labels?.shipping || "Shipping"}</th>
            <th>{labels?.ads || "Ads"}</th>
            <th>{labels?.profit || "Profit"}</th>
            <th>{labels?.margin || "Margin"}</th>
          </tr>
        </thead>
        <tbody>
          {products.map((product) => (
            <tr key={product.product_name}>
              <td>{product.product_name}</td>
              <td>{money(product.revenue)}</td>
              <td>{money(product.cost)}</td>
              <td>{money(product.commission)}</td>
              <td>{money(product.shipping)}</td>
              <td>{money(product.ads_spend)}</td>
              <td className={product.net_profit >= 0 ? "money-positive" : "money-negative"}>
                {money(product.net_profit)}
              </td>
              <td>{product.profit_margin.toFixed(1)}%</td>
            </tr>
          ))}
          {products.length === 0 ? (
            <tr>
              <td colSpan={8} className="muted">{labels?.empty || "No products yet"}</td>
            </tr>
          ) : null}
        </tbody>
      </table>
    </div>
  );
}
