"""
Módulo de Cálculo de Custos - Fichas Aninhadas
Calcula custos recursivamente considerando fichas intermediárias
"""
from decimal import Decimal
from typing import List, Dict, Set, Tuple


def validar_dependencia_circular(db, ficha_id: int, ficha_ingrediente_id: int) -> Tuple[bool, str]:
    """
    Valida se adicionar ficha_ingrediente_id em ficha_id cria loop
    
    Returns:
        (valido, mensagem_erro)
    """
    visitados = set()
    
    def verificar_loop(atual_id: int, target_id: int, caminho: List[str]) -> Tuple[bool, List[str]]:
        if atual_id == target_id:
            return True, caminho
        
        if atual_id in visitados:
            return False, []
        
        visitados.add(atual_id)
        
        # Buscar fichas usadas como ingredientes nesta ficha
        ficha = db.query(FichaTecnica).filter_by(id=atual_id).first()
        if not ficha:
            return False, []
        
        for item in ficha.itens:
            if item.tipo_item == 'ficha' and item.ficha_ingrediente_id:
                sub_ficha = db.query(FichaTecnica).filter_by(id=item.ficha_ingrediente_id).first()
                if sub_ficha:
                    novo_caminho = caminho + [sub_ficha.nome]
                    tem_loop, caminho_loop = verificar_loop(item.ficha_ingrediente_id, target_id, novo_caminho)
                    if tem_loop:
                        return True, caminho_loop
        
        return False, []
    
    # Verificar se adicionar cria loop
    ficha = db.query(FichaTecnica).filter_by(id=ficha_id).first()
    ficha_ingrediente = db.query(FichaTecnica).filter_by(id=ficha_ingrediente_id).first()
    
    if not ficha or not ficha_ingrediente:
        return False, "Ficha não encontrada"
    
    tem_loop, caminho = verificar_loop(ficha_ingrediente_id, ficha_id, [ficha_ingrediente.nome])
    
    if tem_loop:
        caminho_str = " → ".join(caminho + [ficha.nome])
        return False, f"❌ Dependência circular detectada: {caminho_str}"
    
    return True, ""


def calcular_custo_ficha_recursivo(db, ficha_id: int, visitados: Set[int] = None) -> Decimal:
    """
    Calcula custo total de uma ficha recursivamente
    Considera fichas aninhadas e atualiza histórico de custos
    
    Args:
        db: Sessão do banco
        ficha_id: ID da ficha a calcular
        visitados: Set de IDs já visitados (evita loops infinitos)
    
    Returns:
        Custo total em Decimal
    """
    if visitados is None:
        visitados = set()
    
    if ficha_id in visitados:
        # Loop detectado - retorna 0 e não recalcula
        return Decimal('0')
    
    visitados.add(ficha_id)
    
    from models import FichaTecnica, ItemFichaTecnica, Insumo
    
    ficha = db.query(FichaTecnica).filter_by(id=ficha_id).first()
    if not ficha:
        return Decimal('0')
    
    custo_total = Decimal('0')
    
    for item in ficha.itens:
        if item.tipo_item == 'insumo':
            # Item é insumo simples
            insumo = db.query(Insumo).filter_by(id=item.insumo_id).first()
            if insumo:
                # Custo atual do insumo
                custo_item = Decimal(str(insumo.preco_unitario)) * Decimal(str(item.quantidade))
                
                # Atualizar custo histórico (custo/grama atual)
                item.custo_unitario_historico = insumo.preco_unitario
                item.custo_item = custo_item
                
                custo_total += custo_item
        
        elif item.tipo_item == 'ficha':
            # Item é outra ficha técnica
            ficha_ingrediente = db.query(FichaTecnica).filter_by(id=item.ficha_ingrediente_id).first()
            
            if ficha_ingrediente:
                # Calcular custo da ficha ingrediente recursivamente
                custo_ficha_ingrediente = calcular_custo_ficha_recursivo(db, ficha_ingrediente.id, visitados.copy())
                
                # Calcular custo por grama da ficha ingrediente
                rendimento_g = Decimal(str(ficha_ingrediente.rendimento_gramas)) if ficha_ingrediente.rendimento_gramas else Decimal('1')
                
                if rendimento_g > 0:
                    custo_por_grama = custo_ficha_ingrediente / rendimento_g
                else:
                    custo_por_grama = Decimal('0')
                
                # Calcular custo do item (quantidade em gramas)
                quantidade_g = Decimal(str(item.quantidade))
                custo_item = custo_por_grama * quantidade_g
                
                # Atualizar custo histórico
                item.custo_unitario_historico = custo_por_grama
                item.custo_item = custo_item
                
                custo_total += custo_item
    
    # Atualizar custo da ficha
    ficha.custo_insumos = custo_total
    ficha.custo_total = custo_total
    
    db.commit()
    
    return custo_total


def recalcular_todas_fichas(db) -> Dict[str, int]:
    """
    Recalcula custos de TODAS as fichas ativas
    Processa em ordem topológica (fichas sem dependências primeiro)
    
    Returns:
        Dict com estatísticas do processamento
    """
    from models import FichaTecnica
    
    fichas_ativas = db.query(FichaTecnica).filter_by(ativo=1).all()
    
    # Separar fichas por nível de dependência
    fichas_simples = []  # Só usam insumos
    fichas_aninhadas = []  # Usam outras fichas
    
    for ficha in fichas_ativas:
        tem_ficha_ingrediente = any(item.tipo_item == 'ficha' for item in ficha.itens)
        
        if tem_ficha_ingrediente:
            fichas_aninhadas.append(ficha)
        else:
            fichas_simples.append(ficha)
    
    processadas = 0
    erros = 0
    
    # 1. Processar fichas simples primeiro
    for ficha in fichas_simples:
        try:
            calcular_custo_ficha_recursivo(db, ficha.id)
            processadas += 1
        except Exception as e:
            print(f"Erro ao processar ficha {ficha.codigo}: {e}")
            erros += 1
    
    # 2. Processar fichas aninhadas (pode precisar múltiplas passadas)
    max_iteracoes = 10
    iteracao = 0
    
    while fichas_aninhadas and iteracao < max_iteracoes:
        iteracao += 1
        fichas_pendentes = []
        
        for ficha in fichas_aninhadas:
            try:
                calcular_custo_ficha_recursivo(db, ficha.id)
                processadas += 1
            except Exception as e:
                # Se der erro, tenta na próxima iteração
                fichas_pendentes.append(ficha)
        
        fichas_aninhadas = fichas_pendentes
        
        if not fichas_pendentes:
            break
    
    # Fichas que não conseguiram ser processadas
    nao_processadas = len(fichas_aninhadas)
    
    return {
        'processadas': processadas,
        'erros': erros,
        'nao_processadas': nao_processadas,
        'iteracoes': iteracao
    }


def obter_hierarquia_ingredientes(db, ficha_id: int, nivel: int = 0, visitados: Set[int] = None) -> List[Dict]:
    """
    Retorna hierarquia de ingredientes para exibição
    
    Returns:
        Lista de dicts com estrutura hierárquica
    """
    if visitados is None:
        visitados = set()
    
    if ficha_id in visitados:
        return []
    
    visitados.add(ficha_id)
    
    from models import FichaTecnica, Insumo
    
    ficha = db.query(FichaTecnica).filter_by(id=ficha_id).first()
    if not ficha:
        return []
    
    resultado = []
    
    for item in ficha.itens:
        if item.tipo_item == 'insumo':
            insumo = db.query(Insumo).filter_by(id=item.insumo_id).first()
            if insumo:
                resultado.append({
                    'nivel': nivel,
                    'tipo': 'insumo',
                    'nome': insumo.nome,
                    'quantidade': float(item.quantidade),
                    'unidade': insumo.unidade_medida,
                    'custo': float(item.custo_item),
                    'eh_aninhado': False
                })
        
        elif item.tipo_item == 'ficha':
            ficha_ingrediente = db.query(FichaTecnica).filter_by(id=item.ficha_ingrediente_id).first()
            if ficha_ingrediente:
                resultado.append({
                    'nivel': nivel,
                    'tipo': 'ficha',
                    'nome': f"📋 {ficha_ingrediente.nome}",
                    'quantidade': float(item.quantidade),
                    'unidade': 'g',
                    'custo': float(item.custo_item),
                    'eh_aninhado': True
                })
                
                # Adicionar ingredientes da sub-ficha
                sub_itens = obter_hierarquia_ingredientes(db, ficha_ingrediente.id, nivel + 1, visitados.copy())
                resultado.extend(sub_itens)
    
    return resultado
