import { useState, useEffect } from 'react';
import { useReplenishment } from '@/hooks/useReplenishment';
import { ReplenishmentTable } from './ReplenishmentTable';
import type { ReplenishmentItem } from '@/types';

export function ReplenishmentQueue() {
  const { data: initialItems, isLoading, error } = useReplenishment();
  const [items, setItems] = useState<ReplenishmentItem[]>([]);

  // Sync local state with fetched data using useEffect
  useEffect(() => {
    if (initialItems) {
      setItems(initialItems);
    }
  }, [initialItems]);

  const handleApprove = (itemId: string) => {
    setItems((prevItems) =>
      prevItems.map((item) =>
        item.id === itemId ? { ...item, status: 'Approved' as const } : item
      )
    );
  };

  const handleReject = (itemId: string) => {
    setItems((prevItems) =>
      prevItems.map((item) =>
        item.id === itemId ? { ...item, status: 'Rejected' as const } : item
      )
    );
  };

  if (isLoading) {
    return (
      <section className="container mx-auto px-4 py-8">
        <h2 className="text-2xl font-bold text-text-primary mb-6">
          Replenishment Queue
        </h2>
        <div className="bg-card border border-border rounded-lg p-6 h-96 animate-pulse">
          <div className="space-y-3">
            <div className="h-4 bg-card-hover rounded w-full" />
            <div className="h-4 bg-card-hover rounded w-full" />
            <div className="h-4 bg-card-hover rounded w-full" />
            <div className="h-4 bg-card-hover rounded w-3/4" />
          </div>
        </div>
      </section>
    );
  }

  if (error || !items) {
    return (
      <section className="container mx-auto px-4 py-8">
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
          <p className="text-red-400">
            Failed to load replenishment data. Please try again.
          </p>
        </div>
      </section>
    );
  }

  const pendingCount = items.filter((item) => item.status === 'Pending').length;
  const approvedCount = items.filter((item) => item.status === 'Approved').length;

  return (
    <section className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-text-primary mb-2">
          Replenishment Queue
        </h2>
        <p className="text-text-secondary">
          Review and approve restocking recommendations for stores
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-card border border-border rounded-lg p-4">
          <p className="text-xs text-text-secondary uppercase tracking-wide mb-1">
            Pending Review
          </p>
          <p className="text-2xl font-bold text-text-primary">{pendingCount}</p>
        </div>
        <div className="bg-card border border-border rounded-lg p-4">
          <p className="text-xs text-text-secondary uppercase tracking-wide mb-1">
            Approved
          </p>
          <p className="text-2xl font-bold text-green-400">{approvedCount}</p>
        </div>
        <div className="bg-card border border-border rounded-lg p-4">
          <p className="text-xs text-text-secondary uppercase tracking-wide mb-1">
            Total Items
          </p>
          <p className="text-2xl font-bold text-text-primary">{items.length}</p>
        </div>
      </div>

      {/* Table */}
      <div className="bg-card border border-border rounded-lg p-6">
        <ReplenishmentTable
          items={items}
          onApprove={handleApprove}
          onReject={handleReject}
        />
      </div>
    </section>
  );
}
