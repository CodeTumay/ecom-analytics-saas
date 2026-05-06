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
    <div>
      <div className="table-wrap product-table-wrap">
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
      <div className="product-card-list">
        {products.slice(0, 8).map((product) => (
          <article className="product-card-mobile" key={product.product_name}>
            <div className="product-thumb" aria-hidden="true">
              {product.product_name.slice(0, 1).toUpperCase()}
            </div>
            <div className="product-card-copy">
              <div>
                <h3>{product.product_name}</h3>
                <span>{labels?.revenue || "Revenue"}: {money(product.revenue)}</span>
              </div>
              <div className="product-card-metrics">
                <strong className={product.net_profit >= 0 ? "money-positive" : "money-negative"}>
                  {money(product.net_profit)}
                </strong>
                <em>{product.profit_margin.toFixed(1)}%</em>
              </div>
            </div>
          </article>
        ))}
        {products.length === 0 ? <p className="muted">{labels?.empty || "No products yet"}</p> : null}
      </div>
    </div>
  );
}
