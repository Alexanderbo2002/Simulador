from graphviz import Digraph
import os

class BTreeNode:
    def __init__(self, leaf=True):
        self.leaf = leaf
        self.keys = []
        self.children = []

class BTree:
    def __init__(self, order):
        self.order = order
        self.max_keys = order - 1
        self.min_keys = (order // 2)  # Corrección: debe ser orden//2 para nodos no raíz
        self.root = BTreeNode(True)

    def search(self, key, node=None):
        """Busca una clave en el árbol"""
        if node is None:
            node = self.root
        
        i = 0
        # Encuentra la posición donde debería estar la clave
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        
        # Si encontramos la clave, retornar
        if i < len(node.keys) and key == node.keys[i]:
            return (node, i)
        
        # Si es una hoja y no se encontró, no existe
        if node.leaf:
            return None
        
        # Buscar en el hijo correspondiente
        return self.search(key, node.children[i])

    def insert(self, key):
        """Inserta una clave en el árbol"""
        # Verificar duplicados
        if self.search(key) is not None:
            return False
        
        root = self.root
        
        # Si la raíz está llena, dividirla
        if len(root.keys) == self.max_keys:
            new_root = BTreeNode(False)
            new_root.children.append(root)
            self.root = new_root
            self._split_child(new_root, 0)
        
        # Insertar en el árbol no lleno
        self._insert_non_full(self.root, key)
        return True

    def _insert_non_full(self, node, key):
        """Inserta una clave en un nodo que no está lleno"""
        i = len(node.keys) - 1
        
        # Si es una hoja, simplemente insertar en la posición correcta
        if node.leaf:
            # Encontrar la posición correcta
            while i >= 0 and key < node.keys[i]:
                i -= 1
            node.keys.insert(i + 1, key)
        else:
            # Encontrar el hijo en el que debemos insertar
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            
            # Si el hijo está lleno, dividirlo primero
            if len(node.children[i].keys) == self.max_keys:
                self._split_child(node, i)
                # Decidir en qué hijo insertar después de la división
                if key > node.keys[i]:
                    i += 1
            
            # Insertar recursivamente en el hijo
            self._insert_non_full(node.children[i], key)

    def _split_child(self, parent, index):
        """Divide un hijo que está lleno"""
        # El nodo a dividir
        child = parent.children[index]
        
        # Crear un nuevo nodo para la mitad derecha
        new_child = BTreeNode(child.leaf)
        
        # El índice de la clave mediana - corregido
        mid = self.order // 2 - 1
        
        # La clave mediana que subirá al padre
        median_key = child.keys[mid]
        
        # Distribuir las claves
        new_child.keys = child.keys[mid+1:]  # Claves a la derecha
        child.keys = child.keys[:mid]        # Claves a la izquierda
        
        # Si no es hoja, distribuir también los hijos
        if not child.leaf:
            new_child.children = child.children[mid+1:]
            child.children = child.children[:mid+1]
        
        # Insertar la clave mediana en el padre
        parent.keys.insert(index, median_key)
        
        # Insertar el nuevo hijo en el padre
        parent.children.insert(index + 1, new_child)

    def visualize(self):
        """Genera una visualización gráfica del árbol"""
        dot = Digraph(format='png', graph_attr={'rankdir': 'TB'})
        self._node_id = 0
        self._add_nodes(dot, self.root)
        try:
            output_path = os.path.join(os.getcwd(), 'btree')
            dot.render(output_path, cleanup=True)
            print(f"Árbol generado como '{output_path}.png'.")
            return True
        except Exception as e:
            print(f"No se pudo generar la imagen: {e}")
            print("Asegúrese de tener Graphviz instalado correctamente.")
            return False

    def _add_nodes(self, dot, node, parent_name=None):
        """Añade un nodo a la visualización gráfica"""
        current_id = f"node{self._node_id}"
        self._node_id += 1
        
        # Etiqueta con las claves del nodo
        label = f"[{', '.join(map(str, node.keys))}]"
        dot.node(current_id, label)
        
        # Conectar con el padre si existe
        if parent_name is not None:
            dot.edge(parent_name, current_id)
        
        # Procesar recursivamente los hijos
        if not node.leaf:  # Solo si no es una hoja
            for child in node.children:
                self._add_nodes(dot, child, current_id)

    def print_tree(self, node=None, level=0):
        """Imprime la estructura del árbol en formato texto"""
        if node is None:
            node = self.root
            
        print("  " * level, end="")
        print(f"Nivel {level}: {node.keys}")
        
        if not node.leaf:
            for child in node.children:
                self.print_tree(child, level + 1)

    def is_valid(self):
        """Verifica si el árbol cumple todas las propiedades de un árbol B"""
        return self._is_valid(self.root)
        
    def _is_valid(self, node, min_key=float('-inf'), max_key=float('inf'), verbose=True):
        """Verifica recursivamente la validez del árbol"""
        # 1. Todas las claves deben estar ordenadas
        for i in range(1, len(node.keys)):
            if node.keys[i-1] >= node.keys[i]:
                if verbose:
                    print(f"Error: Claves no ordenadas: {node.keys}")
                return False
                
        # 2. Las claves deben estar en el rango correcto
        for key in node.keys:
            if key <= min_key or key >= max_key:
                if verbose:
                    print(f"Error: Clave {key} fuera de rango ({min_key}, {max_key})")
                return False
                
        # 3. Verificar límites de claves por nodo
        if len(node.keys) > self.max_keys:
            if verbose:
                print(f"Error: Nodo con {len(node.keys)} claves, máximo es {self.max_keys}")
            return False
            
        # 4. Todos los nodos excepto la raíz deben tener al menos min_keys
        if node != self.root and len(node.keys) < self.min_keys:
            if verbose:
                print(f"Error: Nodo con {len(node.keys)} claves, mínimo es {self.min_keys}")
            return False
            
        # 5. Un nodo con n claves debe tener n+1 hijos si no es hoja
        if not node.leaf and len(node.children) != len(node.keys) + 1:
            if verbose:
                print(f"Error: Nodo con {len(node.keys)} claves tiene {len(node.children)} hijos")
            return False
            
        # 6. Una hoja no debe tener hijos
        if node.leaf and len(node.children) > 0:
            if verbose:
                print("Error: Nodo hoja tiene hijos")
            return False
            
        # 7. Verificar recursivamente los hijos
        if not node.leaf:
            for i, child in enumerate(node.children):
                # Establecer el rango adecuado para cada hijo
                if i == 0:
                    new_min = min_key
                    new_max = node.keys[0] if len(node.keys) > 0 else max_key
                elif i == len(node.children) - 1:
                    new_min = node.keys[i-1] if i-1 < len(node.keys) else min_key
                    new_max = max_key
                else:
                    new_min = node.keys[i-1] if i-1 < len(node.keys) else min_key
                    new_max = node.keys[i] if i < len(node.keys) else max_key
                
                if not self._is_valid(child, new_min, new_max, verbose):
                    return False
                    
        return True

    def fix_tree(self):
        """Intenta corregir problemas estructurales básicos del árbol"""
        # Eliminar nodos vacíos
        self._remove_empty_nodes(self.root)
        print("Se han intentado corregir problemas estructurales del árbol.")
        return self.is_valid()
    
    def _remove_empty_nodes(self, node):
        """Elimina nodos vacíos recursivamente"""
        if node.leaf:
            return
        
        # Primero corregir hijos recursivamente
        i = 0
        while i < len(node.children):
            child = node.children[i]
            if len(child.keys) == 0 and not child.leaf:
                # Si el hijo está vacío y no es hoja, eliminar y redistribuir sus hijos
                if len(child.children) > 0:
                    node.children.pop(i)  # Eliminar el hijo vacío
                    for grandchild in reversed(child.children):
                        node.children.insert(i, grandchild)  # Insertar nietos en su lugar
                else:
                    node.children.pop(i)  # Simplemente eliminar si no tiene hijos
                continue
            self._remove_empty_nodes(child)
            i += 1

def menu():
    try:
        grado = int(input("Ingrese el grado del árbol B (3, 4, 5, 6, 7): "))
        if grado < 3:
            raise ValueError("El grado del árbol debe ser al menos 3.")
        tree = BTree(grado)
        print(f"Árbol B de grado {grado} creado.")
        print(f"Máximo de claves por nodo: {tree.max_keys}")
        print(f"Mínimo de claves por nodo (excepto raíz): {tree.min_keys}")
    except ValueError as e:
        print(f"Error: {e}")
        return

    while True:
        print("\n1. Insertar\n2. Buscar\n3. Mostrar árbol\n4. Imprimir estructura")
        print("5. Verificar árbol\n6. Intentar corregir árbol\n7. Salir")
        opcion = input("Seleccione una opción: ")
        
        if opcion == '1':
            try:
                entrada = input("Ingrese el valor a insertar (o valores separados por coma): ")
                valores = [int(x.strip()) for x in entrada.split(',')]
                for valor in valores:
                    if tree.insert(valor):
                        print(f"Valor {valor} insertado correctamente.")
                    else:
                        print(f"Valor {valor} ya existe en el árbol.")
            except ValueError:
                print("Por favor, ingrese números válidos.")
        elif opcion == '2':
            try:
                valor = int(input("Ingrese el valor a buscar: "))
                resultado = tree.search(valor)
                if resultado:
                    nodo, pos = resultado
                    print(f"Valor {valor} encontrado en el árbol en la posición {pos} de un nodo con claves {nodo.keys}.")
                else:
                    print(f"Valor {valor} no encontrado.")
            except ValueError:
                print("Por favor, ingrese un número válido.")
        elif opcion == '3':
            if not tree.visualize():
                print("Sugerencia: Si está en un entorno sin Graphviz, pruebe la opción 4 para ver la estructura en texto.")
        elif opcion == '4':
            print("\nEstructura del árbol:")
            tree.print_tree()
        elif opcion == '5':
            if tree.is_valid():
                print("El árbol es válido y cumple con todas las propiedades de un árbol B.")
            else:
                print("El árbol NO es válido. Tiene problemas estructurales.")
                print("Puede usar la opción 6 para intentar corregir automáticamente los problemas.")
        elif opcion == '6':
            if tree.fix_tree():
                print("Árbol corregido exitosamente.")
            else:
                print("No se pudieron corregir todos los problemas del árbol.")
        elif opcion == '7':
            print("Saliendo...")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    menu()