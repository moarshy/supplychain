import { useState, useEffect } from 'react';
import { api } from '../../services/api';
import type { Transaction } from '../../services/api';

export function useTransactions() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.transactions.getAll();
      setTransactions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch transactions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, []);

  const createTransaction = async (transaction: Partial<Transaction>): Promise<Transaction | null> => {
    try {
      setError(null);
      const newTransaction = await api.transactions.create(transaction);
      setTransactions(prev => [newTransaction, ...prev]);
      return newTransaction;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create transaction');
      return null;
    }
  };

  const createBatchTransactions = async (transactions: Partial<Transaction>[]): Promise<Transaction[] | null> => {
    try {
      setError(null);
      const newTransactions = await api.transactions.createBatch(transactions);
      setTransactions(prev => [...newTransactions, ...prev]);
      return newTransactions;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create batch transactions');
      return null;
    }
  };

  return {
    transactions,
    loading,
    error,
    refetch: fetchTransactions,
    createTransaction,
    createBatchTransactions,
  };
}