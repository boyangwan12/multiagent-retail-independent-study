import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  flexRender,
  createColumnHelper,
  type SortingState,
} from '@tanstack/react-table';
import { ArrowUpDown } from 'lucide-react';
import { useState } from 'react';

interface ClusterMape {
  clusterName: string;
  mape: number;
  bias: number;
  accuracy: number;
}

interface MapeByClusterTableProps {
  data: ClusterMape[];
}

const columnHelper = createColumnHelper<ClusterMape>();

export function MapeByClusterTable({ data }: MapeByClusterTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);

  const columns = [
    columnHelper.accessor('clusterName', {
      header: 'Cluster',
      cell: (info) => (
        <span className="font-medium text-text-primary">{info.getValue()}</span>
      ),
    }),
    columnHelper.accessor('mape', {
      header: ({ column }) => (
        <button
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className="flex items-center gap-1 hover:text-text-primary transition-colors"
        >
          MAPE (%)
          <ArrowUpDown className="h-3 w-3" />
        </button>
      ),
      cell: (info) => {
        const mape = info.getValue();
        const color = mape < 15 ? 'text-success' : mape < 20 ? 'text-warning' : 'text-error';
        return <span className={`font-mono ${color}`}>{mape.toFixed(1)}%</span>;
      },
    }),
    columnHelper.accessor('bias', {
      header: ({ column }) => (
        <button
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className="flex items-center gap-1 hover:text-text-primary transition-colors"
        >
          Bias (%)
          <ArrowUpDown className="h-3 w-3" />
        </button>
      ),
      cell: (info) => {
        const bias = info.getValue();
        const color = Math.abs(bias) < 3 ? 'text-success' : Math.abs(bias) < 5 ? 'text-warning' : 'text-error';
        return (
          <span className={`font-mono ${color}`}>
            {bias > 0 ? '+' : ''}{bias.toFixed(1)}%
          </span>
        );
      },
    }),
    columnHelper.accessor('accuracy', {
      header: ({ column }) => (
        <button
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className="flex items-center gap-1 hover:text-text-primary transition-colors"
        >
          Accuracy (%)
          <ArrowUpDown className="h-3 w-3" />
        </button>
      ),
      cell: (info) => (
        <span className="font-mono text-text-primary">{info.getValue().toFixed(1)}%</span>
      ),
    }),
  ];

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
    },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  return (
    <div className="bg-card border border-border rounded-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-background border-b border-border">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider"
                  >
                    {header.isPlaceholder
                      ? null
                      : flexRender(header.column.columnDef.header, header.getContext())}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="divide-y divide-border">
            {table.getRowModel().rows.map((row) => (
              <tr key={row.id} className="hover:bg-hover transition-colors">
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-6 py-4 whitespace-nowrap text-sm">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary */}
      <div className="px-6 py-4 bg-background border-t border-border">
        <p className="text-text-secondary text-xs">
          <span className="text-success">● Good</span> (MAPE &lt;15%, Bias &lt;3%)
          <span className="ml-4 text-warning">● Fair</span> (MAPE 15-20%, Bias 3-5%)
          <span className="ml-4 text-error">● Needs Improvement</span> (MAPE &gt;20%, Bias &gt;5%)
        </p>
      </div>
    </div>
  );
}
