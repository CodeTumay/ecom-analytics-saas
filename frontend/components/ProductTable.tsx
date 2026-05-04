import type { ProductRow } from "@/lib/api";

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0
});

export function ProductTable({ products }: { products: ProductRow[] }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Product</th>
            <th>Revenue</th>
            <th>Cost</th>
            <th>Commission</th>
            <th>Shipping</th>
            <th>Ads</th>
            <th>Profit</th>
            <th>Margin</th>
          </tr>
        </thead>
        <tbody>
          {products.map((product) => (
            <tr key={product.product_name}>
              <td>{product.product_name}</td>
              <td>{money.format(product.revenue)}</td>
              <td>{money.format(product.cost)}</td>
              <td>{money.format(product.commission)}</td>
              <td>{money.format(product.shipping)}</td>
              <td>{money.format(product.ads_spend)}</td>
              <td className={product.net_profit >= 0 ? "money-positive" : "money-negative"}>
                {money.format(product.net_profit)}
              </td>
              <td>{product.profit_margin.toFixed(1)}%</td>
            </tr>
          ))}
          {products.length === 0 ? (
            <tr>
              <td colSpan={8} className="muted">No products yet</td>
            </tr>
          ) : null}
        </tbody>
      </table>
    </div>
  );
}
