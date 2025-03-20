from graphviz import Digraph
import os

class BTreeNode:
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []
        self.children = []

class BTree:
    def __init__(self, order):
        self.order = order
        self.max_keys = order - 1
        self.root = BTreeNode(True)

    def insert(self, key):
        root = self.root
        if len(root.keys) == self.max_keys:
            new_root = BTreeNode(False)
            new_root.children.append(self.root)
            self.split_child(new_root, 0)
            self.root = new_root
        self._insert_non_full(self.root, key)

    def _insert_non_full(self, node, key):
        i = len(node.keys) - 1
        if node.leaf:
            # Inserta ordenadamente en las hojas
            while i >= 0 and key < node.keys[i]:
                i -= 1
            node.keys.insert(i + 1, key)
        else:
            # Encuentra el hijo correcto
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            
            # Si el hijo está lleno, divídelo
            if len(node.children[i].keys) == self.max_keys:
                self.split_child(node, i)
                # Después de dividir, tenemos que determinar cuál hijo usar
                if key > node.keys[i]:
                    i += 1
            
            # Inserta en el hijo correcto
            self._insert_non_full(node.children[i], key)

    def split_child(self, parent, i):
        # Obtiene el nodo a dividir
        child = parent.children[i]
        
        # Calcula el índice medio basado en el orden del árbol
        mid_index = (self.max_keys) // 2
        
        # Crea dos nuevos nodos
        left_child = BTreeNode(child.leaf)
        right_child = BTreeNode(child.leaf)
        
        # Distribuye las claves correctamente
        left_child.keys = child.keys[:mid_index]
        median = child.keys[mid_index]  # Este valor sube al padre
        right_child.keys = child.keys[mid_index + 1:]
        
        # Si no es hoja, distribuye también los hijos
        if not child.leaf:
            left_child.children = child.children[:mid_index + 1]
            right_child.children = child.children[mid_index + 1:]
        
        # Inserta la mediana en el padre en la posición correcta
        parent.keys.insert(i, median)
        
        # Reemplaza el hijo original con los dos nuevos
        parent.children[i] = left_child
        parent.children.insert(i + 1, right_child)

    def remove(self, key):
        pass  # Aún sin implementar

    def visualize(self):
        dot = Digraph(format='png', graph_attr={'rankdir': 'TB'})
        self._node_id = 0
        self._add_nodes(dot, self.root)
        try:
            output_path = os.path.join(os.getcwd(), 'btree')
            dot.render(output_path, cleanup=True)
            print(f"Árbol generado como '{output_path}.png'.")
        except OSError as e:
            print(f"No se pudo generar la imagen: {e}")

    def _add_nodes(self, dot, node, parent_name=None):
        current_id = f"node{self._node_id}"
        self._node_id += 1
        dot.node(current_id, f"[{', '.join(map(str, node.keys))}]")
        if parent_name is not None:
            dot.edge(parent_name, current_id)
        for child in node.children:
            self._add_nodes(dot, child, current_id)

def menu():
    try:
        grado = int(input("Ingrese el grado del árbol B (3, 4, 5, 6, 7): "))
        if grado not in [3, 4, 5, 6, 7]:
            raise ValueError("El grado del árbol debe ser 3, 4, 5, 6 o 7.")
        tree = BTree(grado)
    except ValueError as e:
        print(f"Error: {e}")
        return

    while True:
        print("\n1. Insertar\n2. Eliminar\n3. Mostrar árbol\n4. Salir")
        opcion = input("Seleccione una opción: ")
        
        if opcion == '1':
            try:
                entrada = input("Ingrese el valor a insertar (o valores separados por coma): ")
                valores = [int(x.strip()) for x in entrada.split(',')]
                for valor in valores:
                    tree.insert(valor)
                print("Valor(es) insertado(s) correctamente.")
            except ValueError:
                print("Por favor, ingrese números válidos.")
        elif opcion == '2':
            try:
                valor = int(input("Ingrese el valor a eliminar: "))
                tree.remove(valor)  # Aún sin implementar
                print("Valor eliminado correctamente.")
            except ValueError:
                print("Por favor, ingrese un número válido.")
        elif opcion == '3':
            tree.visualize()
        elif opcion == '4':
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    menu()