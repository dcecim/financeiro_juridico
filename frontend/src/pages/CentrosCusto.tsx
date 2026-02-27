import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Edit2, Trash2, FolderTree, ChevronRight, ChevronDown } from 'lucide-react';
import { centrosCustoService } from '../services/centrosCusto';
import { CentroCusto } from '../services/types';
import { CentroCustoModal } from '../components/CentroCustoModal';

interface CentroCustoNode extends CentroCusto {
  children: CentroCustoNode[];
}

export default function CentrosCusto() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<CentroCusto | null>(null);
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  
  const queryClient = useQueryClient();

  const { data: centrosCusto, isLoading } = useQuery({
    queryKey: ['centrosCusto'],
    queryFn: () => centrosCustoService.getAll()
  });

  const deleteMutation = useMutation({
    mutationFn: centrosCustoService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['centrosCusto'] });
    }
  });

  const handleDelete = async (id: string) => {
    if (window.confirm('Tem certeza que deseja excluir este centro de custo?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleEdit = (item: CentroCusto) => {
    setEditingItem(item);
    setIsModalOpen(true);
  };

  const handleAdd = (parent?: CentroCusto) => {
    setEditingItem(parent ? { parent_id: parent.id } as CentroCusto : null);
    setIsModalOpen(true);
  };

  const toggleExpand = (id: string) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedItems(newExpanded);
  };

  const treeData = useMemo(() => {
    if (!centrosCusto) return [];
    
    const map = new Map<string, CentroCustoNode>();
    const roots: CentroCustoNode[] = [];

    // Initialize map
    centrosCusto.forEach(item => {
      map.set(item.id, { ...item, children: [] });
    });

    // Build tree
    centrosCusto.forEach(item => {
      const node = map.get(item.id)!;
      if (item.parent_id && map.has(item.parent_id)) {
        map.get(item.parent_id)!.children.push(node);
      } else {
        roots.push(node);
      }
    });

    return roots;
  }, [centrosCusto]);

  const renderTreeItem = (item: CentroCustoNode, level: number = 0) => {
    const hasChildren = item.children.length > 0;
    const isExpanded = expandedItems.has(item.id);

    return (
      <div key={item.id} className="select-none">
        <div 
          className={`flex items-center justify-between p-3 hover:bg-gray-50 border-b ${level > 0 ? 'ml-6 border-l pl-4' : ''}`}
        >
          <div className="flex items-center gap-2 flex-1">
            {hasChildren ? (
              <button 
                onClick={() => toggleExpand(item.id)}
                className="p-1 hover:bg-gray-200 rounded"
              >
                {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
              </button>
            ) : (
              <div className="w-6" />
            )}
            <span className="font-mono text-sm text-gray-500 bg-gray-100 px-1 rounded mr-2">
              {item.codigo || '------'}
            </span>
            <span className="font-medium">{item.nome}</span>
            {item.descricao && (
              <span className="text-sm text-gray-400 ml-2 hidden md:inline-block">- {item.descricao}</span>
            )}
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <span className="hidden md:inline-block font-mono text-xs mr-4" title="UUID">
              {item.id.substring(0, 8)}...
            </span>
            <button 
              onClick={() => handleAdd(item)}
              className="p-1 hover:bg-green-100 text-green-600 rounded"
              title="Adicionar Subcategoria"
            >
              <Plus size={16} />
            </button>
            <button 
              onClick={() => handleEdit(item)}
              className="p-1 hover:bg-blue-100 text-blue-600 rounded"
              title="Editar"
            >
              <Edit2 size={16} />
            </button>
            <button
              onClick={() => handleDelete(item.id)}
              className="p-2 text-red-600 hover:bg-red-50 rounded-full"
              title="Excluir"
            >
              <Trash2 size={18} />
            </button>
          </div>
        </div>

        {hasChildren && isExpanded && (
          <div className="border-l border-gray-200 ml-3">
            {item.children.map(child => renderTreeItem(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  if (isLoading) return <div className="p-8 text-center">Carregando...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <FolderTree className="w-8 h-8" />
          Centros de Custo
        </h1>
        <button
          onClick={() => handleAdd()}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700 transition-colors"
        >
          <Plus size={20} />
          Nova Categoria
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 border-b bg-gray-50 font-medium text-gray-600">
          Estrutura de Categorias
        </div>
        <div className="divide-y divide-gray-100">
          {treeData.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              Nenhum centro de custo cadastrado.
            </div>
          ) : (
            treeData.map(root => renderTreeItem(root))
          )}
        </div>
      </div>

      <CentroCustoModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setEditingItem(null);
        }}
        initialData={editingItem}
        parentOptions={centrosCusto || []}
      />
    </div>
  );
}
